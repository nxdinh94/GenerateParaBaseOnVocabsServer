from fastapi import APIRouter, HTTPException, Depends, Header
from app.api.v1 import schemas
from app.api.v1.database_routes import router as db_router
from app.services.openai_client import OpenAIClient
from app.services.gemini_client import GeminiClient
from app.services.claude_client import ClaudeClient
from app.services.google_auth import google_auth_service
from app.database.crud import get_user_crud, get_refresh_token_crud
from app.database.models import GoogleUserCreate, RefreshTokenCreate
from app.utils.logging_conf import get_logger
from typing import Optional
from datetime import datetime
from bson import ObjectId

logger = get_logger("routes")
router = APIRouter(prefix="/api/v1", tags=["v1"])

# Include database routes
router.include_router(db_router)

gemini_client = GeminiClient()
openai_client = OpenAIClient()
claude_client = ClaudeClient()

# === Google Authentication ===
@router.post("/auth/google/login", response_model=schemas.GoogleLoginResponse)
async def google_login(req: schemas.GoogleLoginRequest):
    """
    Handle Google OAuth login using authorization code from React app
    """
    try:
        logger.info(f"🔄 Starting Google login with code: {req.authorization_code[:20]}...")
        
        # Try different redirect URIs that might have been used
        redirect_uris_to_try = [
            "http://localhost:5173",  # Vite default
            "http://localhost:3000",  # React default  
            "postmessage",            # For popup mode
            "urn:ietf:wg:oauth:2.0:oob"  # For desktop/mobile
        ]
        
        auth_result = None
        last_error = None
        
        for redirect_uri in redirect_uris_to_try:
            try:
                logger.info(f"🔄 Trying redirect_uri: {redirect_uri}")
                auth_result = await google_auth_service.exchange_code_for_tokens(
                    req.authorization_code, 
                    redirect_uri
                )
                logger.info(f"✅ Success with redirect_uri: {redirect_uri}")
                break
            except Exception as e:
                logger.warning(f"❌ Failed with redirect_uri {redirect_uri}: {str(e)}")
                last_error = e
                continue
        
        if not auth_result:
            error_message = str(last_error) if last_error else "All redirect_uri attempts failed"
            
            # Check for specific Google errors and return appropriate HTTP status
            if "invalid_grant" in error_message.lower():
                raise HTTPException(status_code=400, detail={
                    "error": "invalid_authorization_code",
                    "message": "Authorization code is invalid, expired, or already used",
                    "details": error_message
                })
            elif "invalid_client" in error_message.lower():
                raise HTTPException(status_code=401, detail={
                    "error": "invalid_client_credentials", 
                    "message": "Google OAuth client credentials are invalid",
                    "details": error_message
                })
            elif "unauthorized_client" in error_message.lower():
                raise HTTPException(status_code=403, detail={
                    "error": "unauthorized_client",
                    "message": "Client is not authorized for this operation", 
                    "details": error_message
                })
            else:
                raise HTTPException(status_code=500, detail={
                    "error": "authentication_failed",
                    "message": "Google authentication failed",
                    "details": error_message
                })
        
        user_info = auth_result["user_info"]
        
        # Save or update user in database
        user_crud = get_user_crud()
        refresh_token_crud = get_refresh_token_crud()
        
        # Check if user already exists
        existing_user = await user_crud.get_user_by_google_id(user_info.get("id"))
        
        if existing_user:
            # Update existing user with latest info
            updated_user = await user_crud.update_google_user(user_info.get("id"), user_info)
            user_db = updated_user
            logger.info(f"🔄 Updated existing Google user: {user_info.get('email')}")
        else:
            # Create new user
            google_user_data = GoogleUserCreate(
                google_id=user_info.get("id"),
                name=user_info.get("name"),
                email=user_info.get("email"),
                picture=user_info.get("picture"),
                verified_email=user_info.get("verified_email")
            )
            user_db = await user_crud.create_google_user(google_user_data)
            logger.info(f"✅ Created new Google user: {user_info.get('email')}")
        
        # Check if user has a default vocabulary collection, create one if not
        from app.database.crud import get_vocab_collection_crud
        from app.database.models import VocabCollectionCreate, UserUpdate
        
        vocab_collection_crud = get_vocab_collection_crud()
        user_collections = await vocab_collection_crud.get_user_vocab_collections(str(user_db.id))
        
        if not user_collections:
            # Create default "Default" collection for new user
            default_collection_data = VocabCollectionCreate(
                name="Default",
                user_id=str(user_db.id)
            )
            default_collection = await vocab_collection_crud.create_vocab_collection(default_collection_data)
            logger.info(f"📚 Created default vocabulary collection for user: {user_db.email} (Collection ID: {default_collection.id})")
            
            # Set the selected_collection_id to the default collection
            update_data = UserUpdate(
                name=None,
                email=None,
                avt=None
            )
            await user_crud.collection.update_one(
                {"_id": ObjectId(str(user_db.id))},
                {"$set": {"selected_collection_id": str(default_collection.id)}}
            )
            logger.info(f"📚 Set selected_collection_id to default collection for user: {user_db.email}")
        else:
            logger.info(f"📚 User {user_db.email} already has {len(user_collections)} vocabulary collection(s)")
            
            # If user doesn't have selected_collection_id set, set it to the first collection
            if not user_db.selected_collection_id:
                await user_crud.collection.update_one(
                    {"_id": ObjectId(str(user_db.id))},
                    {"$set": {"selected_collection_id": str(user_collections[0].id)}}
                )
                logger.info(f"📚 Set selected_collection_id to first collection for user: {user_db.email}")
        
        # Fetch updated user to get the selected_collection_id
        user_db = await user_crud.get_user_by_id(str(user_db.id))
        
        # Create JWT token for our application (using database user ID)
        jwt_user_data = {
            "id": str(user_db.id),  # Use database user ID (_id) as primary identifier
            "user_id": str(user_db.id),  # Keep for backward compatibility
            "google_id": user_db.google_id,  # Store Google ID for reference
            "email": user_db.email,
            "name": user_db.name,
            "picture": user_db.picture,
            "verified_email": user_db.verified_email,
            "selected_collection_id": user_db.selected_collection_id  # Include selected collection
        }
        jwt_token = google_auth_service.create_jwt_token(jwt_user_data)
        
        # Create JWT refresh token for renewing JWT tokens
        jwt_refresh_token = google_auth_service.create_jwt_refresh_token(jwt_user_data)
        
        # Save JWT refresh token to database
        refresh_token_data = RefreshTokenCreate(
            user_id=str(user_db.id),
            refresh_token=jwt_refresh_token
        )
        await refresh_token_crud.create_refresh_token(refresh_token_data)
        logger.info(f"💾 Saved JWT refresh token for user: {user_db.email}")
        
        logger.info(f"✅ User {user_info.get('email')} logged in successfully")
        
        return schemas.GoogleLoginResponse(
            jwt_token=jwt_token,
            jwt_refresh_token=jwt_refresh_token
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        logger.exception("❌ Unexpected error during Google login")
        raise HTTPException(status_code=500, detail={
            "error": "internal_server_error",
            "message": "An unexpected error occurred during authentication",
            "details": str(e)
        })

@router.post("/auth/debug-exchange")
async def debug_token_exchange(req: schemas.GoogleLoginRequest):
    """
    Debug endpoint to test token exchange with detailed logging
    """
    try:
        logger.info(f"🐛 DEBUG: Starting token exchange debug")
        logger.info(f"🐛 Authorization code length: {len(req.authorization_code)}")
        logger.info(f"🐛 Code starts with: {req.authorization_code[:10]}...")
        
        # Get service config
        logger.info(f"🐛 Client ID: {google_auth_service.client_id[:20]}..." if google_auth_service.client_id else "🐛 NO CLIENT ID")
        logger.info(f"🐛 Client Secret: {'SET' if google_auth_service.client_secret else 'NOT SET'}")
        logger.info(f"🐛 Redirect URI: {google_auth_service.redirect_uri}")
        
        # Try the exchange
        auth_result = await google_auth_service.exchange_code_for_tokens(req.authorization_code)
        
        return {
            "status": True,
            "message": "Debug exchange successful",
            "debug_info": {
                "client_id_set": bool(google_auth_service.client_id),
                "client_secret_set": bool(google_auth_service.client_secret),
                "redirect_uri": google_auth_service.redirect_uri,
                "code_length": len(req.authorization_code)
            },
            "result": "Success"
        }
        
    except Exception as e:
        logger.exception("🐛 DEBUG: Token exchange failed")
        
        error_message = str(e)
        if "invalid_grant" in error_message.lower():
            raise HTTPException(status_code=400, detail={
                "error": "debug_invalid_grant",
                "message": "Debug: Authorization code is invalid or expired",
                "debug_info": {
                    "client_id_set": bool(google_auth_service.client_id),
                    "client_secret_set": bool(google_auth_service.client_secret),
                    "redirect_uri": google_auth_service.redirect_uri,
                    "code_length": len(req.authorization_code) if req.authorization_code else 0
                },
                "details": error_message
            })
        else:
            raise HTTPException(status_code=500, detail={
                "error": "debug_exchange_failed",
                "message": "Debug: Token exchange failed",
                "debug_info": {
                    "client_id_set": bool(google_auth_service.client_id),
                    "client_secret_set": bool(google_auth_service.client_secret),
                    "redirect_uri": google_auth_service.redirect_uri,
                    "code_length": len(req.authorization_code) if req.authorization_code else 0
                },
                "details": error_message
            })

@router.post("/auth/verify-token", response_model=schemas.TokenVerifyResponse)
async def verify_token(req: schemas.TokenVerifyRequest):
    """
    Verify JWT token and return user data
    """
    try:
        if not req.token or req.token.strip() == "":
            raise HTTPException(status_code=400, detail={
                "error": "missing_token",
                "message": "Token is required"
            })
            
        user_data = google_auth_service.verify_jwt_token(req.token)
        
        if user_data:
            return schemas.TokenVerifyResponse(
                status=True,
                message="Token is valid",
                user_data=user_data
            )
        else:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_token",
                "message": "Token is invalid or expired"
            })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error verifying token")
        raise HTTPException(status_code=500, detail={
            "error": "token_verification_failed",
            "message": "Failed to verify token",
            "details": str(e)
        })

@router.post("/auth/refresh-token", response_model=schemas.RefreshTokenResponse)
async def refresh_token(req: schemas.RefreshTokenRequest):
    """
    Refresh Google access token using refresh token
    """
    try:
        if not req.refresh_token or req.refresh_token.strip() == "":
            raise HTTPException(status_code=400, detail={
                "error": "missing_refresh_token",
                "message": "Refresh token is required"
            })
            
        token_data = await google_auth_service.refresh_access_token(req.refresh_token)
        
        return schemas.RefreshTokenResponse(
            status=True,
            message="Token refreshed successfully",
            access_token=token_data.get("access_token"),
            expires_in=token_data.get("expires_in")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error refreshing token")
        error_message = str(e).lower()
        
        if "invalid_grant" in error_message or "invalid refresh token" in error_message:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_refresh_token",
                "message": "Refresh token is invalid or expired"
            })
        else:
            raise HTTPException(status_code=500, detail={
                "error": "token_refresh_failed",
                "message": "Failed to refresh token",
                "details": str(e)
            })

@router.post("/auth/renew-jwt", response_model=schemas.RenewJWTResponse)
async def renew_jwt_token(req: schemas.RenewJWTRequest):
    """
    Renew JWT token using JWT refresh token
    """
    try:
        if not req.jwt_refresh_token or req.jwt_refresh_token.strip() == "":
            raise HTTPException(status_code=400, detail={
                "error": "missing_jwt_refresh_token",
                "message": "JWT refresh token is required"
            })
        
        refresh_token_crud = get_refresh_token_crud()
        
        # Verify JWT refresh token exists in database
        stored_refresh_token = await refresh_token_crud.get_refresh_token_by_token(req.jwt_refresh_token)
        
        if not stored_refresh_token:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_jwt_refresh_token",
                "message": "JWT refresh token not found in database"
            })
            
        # Verify JWT refresh token signature and expiration
        user_data = google_auth_service.verify_jwt_refresh_token(req.jwt_refresh_token)
        
        if not user_data:
            # Remove invalid token from database
            await refresh_token_crud.delete_refresh_token(req.jwt_refresh_token)
            raise HTTPException(status_code=401, detail={
                "error": "invalid_jwt_refresh_token",
                "message": "JWT refresh token is invalid or expired"
            })
        
        # Fetch latest user data from database to get current selected_collection_id
        user_crud = get_user_crud()
        user_id = user_data.get("user_id") or user_data.get("id")
        user_db = await user_crud.get_user_by_id(user_id)
        
        if user_db:
            # Update user_data with latest selected_collection_id from database
            user_data["selected_collection_id"] = user_db.selected_collection_id
        
        # Create new JWT token with updated user data
        new_jwt_token = google_auth_service.create_jwt_token(user_data)
        
        logger.info(f"✅ JWT token renewed for user: {user_data.get('email')}")
        
        return schemas.RenewJWTResponse(
            status=True,
            message="JWT token renewed successfully",
            jwt_token=new_jwt_token,
            user_data={
                "user_id": user_data.get("user_id"),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "picture": user_data.get("picture"),
                "selected_collection_id": user_data.get("selected_collection_id")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error renewing JWT token")
        raise HTTPException(status_code=500, detail={
            "error": "jwt_renewal_failed",
            "message": "Failed to renew JWT token",
            "details": str(e)
        })

@router.get("/auth/profile")
async def get_user_profile(authorization: Optional[str] = Header(None)):
    """
    Get user profile from JWT token in Authorization header
    """
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail={
                "error": "missing_authorization_header",
                "message": "Authorization header is required"
            })
            
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail={
                "error": "invalid_authorization_format",
                "message": "Authorization header must be in format: Bearer <token>"
            })
        
        token = authorization.split(" ")[1]
        user_data = google_auth_service.verify_jwt_token(token)
        
        if user_data:
            return {
                "status": True,
                "message": "Profile retrieved successfully",
                "user_data": user_data
            }
        else:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_token",
                "message": "Token is invalid or expired"
            })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting user profile")
        raise HTTPException(status_code=500, detail={
            "error": "profile_retrieval_failed",
            "message": "Failed to retrieve user profile",
            "details": str(e)
        })

# Helper function to get current user from JWT token
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to get current user from JWT token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail={
            "error": "missing_authorization_header",
            "message": "Authorization header is required"
        })
        
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={
            "error": "invalid_authorization_format", 
            "message": "Authorization header must be in format: Bearer <token>"
        })
    
    token = authorization.split(" ")[1]
    user_data = google_auth_service.verify_jwt_token(token)
    
    if not user_data:
        raise HTTPException(status_code=401, detail={
            "error": "invalid_token",
            "message": "Token is invalid or expired"
        })
    
    return user_data

@router.post("/auth/logout", response_model=schemas.LogoutResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user by deleting all JWT refresh tokens from database
    Requires Bearer token in Authorization header
    """
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token (missing both 'user_id' and 'id' fields)"
            })
        
        refresh_token_crud = get_refresh_token_crud()
        
        # Delete all refresh tokens for this user
        deleted_count = await refresh_token_crud.delete_user_refresh_tokens(user_id)
        
        logger.info(f"🚪 User {current_user.get('email')} logged out. Deleted {deleted_count} refresh tokens.")
        
        return schemas.LogoutResponse(
            status=True,
            message=f"Logout successful. {deleted_count} refresh token(s) deleted."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error during logout")
        raise HTTPException(status_code=500, detail={
            "error": "logout_failed",
            "message": "Failed to logout user",
            "details": str(e)
        })

@router.post("/change-selected-collection", response_model=schemas.ChangeSelectedCollectionResponse)
async def change_selected_collection(req: schemas.ChangeSelectedCollectionRequest, current_user: dict = Depends(get_current_user)):
    """
    Change user's selected vocabulary collection
    Requires Bearer token in Authorization header
    """
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token (missing both 'user_id' and 'id' fields)"
            })
        
        # Validate collection_id
        if not req.selected_collection_id or req.selected_collection_id.strip() == "":
            raise HTTPException(status_code=400, detail={
                "error": "missing_collection_id",
                "message": "selected_collection_id is required"
            })
        
        # Verify collection exists and belongs to user
        from app.database.crud import get_vocab_collection_crud
        vocab_collection_crud = get_vocab_collection_crud()
        
        collection = await vocab_collection_crud.get_vocab_collection_by_id(req.selected_collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail={
                "error": "collection_not_found",
                "message": "Vocabulary collection not found"
            })
        
        if str(collection.user_id) != user_id:
            raise HTTPException(status_code=403, detail={
                "error": "access_denied",
                "message": "You can only select your own vocabulary collections"
            })
        
        # Update user's selected collection
        user_crud = get_user_crud()
        updated_user = await user_crud.update_selected_collection(user_id, req.selected_collection_id)
        
        if not updated_user:
            raise HTTPException(status_code=500, detail={
                "error": "update_failed",
                "message": "Failed to update selected collection"
            })
        
        logger.info(f"✅ User {current_user.get('email')} changed selected collection to {req.selected_collection_id}")
        
        return schemas.ChangeSelectedCollectionResponse(
            status=True,
            message="Selected collection updated successfully",
            selected_collection_id=req.selected_collection_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error changing selected collection")
        raise HTTPException(status_code=500, detail={
            "error": "update_failed",
            "message": "Failed to change selected collection",
            "details": str(e)
        })


# === Paragraph with vocabularies ===
@router.post("/generate-paragraph", response_model=schemas.ParagraphResponse)
async def generate_paragraph(req: schemas.ParagraphRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Validate required fields
        if not req.language or req.language.strip() == "":
            raise HTTPException(status_code=400, detail={
                "error": "missing_language",
                "message": "Language is required"
            })
            
        if not req.vocabularies or len(req.vocabularies) == 0:
            raise HTTPException(status_code=400, detail={
                "error": "missing_vocabularies", 
                "message": "At least one vocabulary is required"
            })
            
        if not req.level or req.level.strip() == "":
            raise HTTPException(status_code=400, detail={
                "error": "missing_level",
                "message": "Level is required"
            })
            
        # Validate length
        if req.length and req.length <= 0:
            raise HTTPException(status_code=400, detail={
                "error": "invalid_length",
                "message": "Length must be a positive number"
            })
        
        paragraphLength = req.length if req.length and req.length > 0 else 1
        print(paragraphLength)
        print(paragraphLength)
        base_prompt = (
            f"Write {'one meaningful sentence' if paragraphLength == 1 else f'one meaningful paragraph of {paragraphLength} words'} "
            f"in {req.language}, at {req.level} level, with a {req.tone} tone, "
            f"about the topic: {req.topic if req.topic else 'beginner'}. "
            f"The text must include all of the following vocabularies at least once: {', '.join(req.vocabularies)}. "
            f"Only highlight each vocabulary in **bold** in the text, ignore all other text. Don't hightlight 'none' word\n\n"
            f"Then, for each vocabulary:\n"
            f"1. Provide phonetic transcription and part of speech.\n"
            f"2. List all meanings based on the Cambridge Dictionary, and give one example for each meaning.\n"
            f"3. Indicate which specific meaning is used in the generated text.\n\n"
            f"Return the final result strictly in the following JSON format:\n"
            f"{{\n"
            f'  "paragraph": "<the generated text>",\n'
            f'  "explain_vocabs": {{\n'
            f'    "vocabulary_1": [\n'
            f'      {{ "phonetic_transcription": "<IPA>", "part_of_speech": "<pos>" }},\n'
            f'      {{ "meaning": "<meaning 1>", "example": "<example sentence>" }},\n'
            f'      {{ "meaning": "<meaning 2>", "example": "<example sentence>" }}\n'
            f'    ],\n'
            f'    "vocabulary_2": [\n'
            f'      {{ "phonetic_transcription": "<IPA>", "part_of_speech": "<pos>" }},\n'
            f'      {{ "meaning": "<meaning>", "example": "<example sentence>" }}\n'
            f'    ]\n'
            f'  }},\n'
            f'  "explanation_in_paragraph": {{\n'
            f'    "vocabulary_1": "explanation of the meaning used in the paragraph (highlight the vocabulary in **bold**)",\n'
            f'    "vocabulary_2": "explanation of the meaning used in the paragraph (highlight the vocabulary in **bold**)"\n'
            f'  }}\n'
            f"}}"
        )

        if req.prompt:
            final_prompt = f"{base_prompt}\nAdditional instruction: {req.prompt}"
        else:
            final_prompt = base_prompt

        # res_text = await openai_client.generate_text(final_prompt)
        res_text = await gemini_client.generate_text(final_prompt)
        
        return schemas.ParagraphResponse(result=res_text, status=True)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating paragraph")
        raise HTTPException(status_code=500, detail={
            "error": "paragraph_generation_failed",
            "message": "Failed to generate paragraph",
            "details": str(e)
        })

# === Save paragraph and vocabularies ===
@router.post("/save-paragraph", response_model=schemas.SaveParagraphResponse)
async def save_paragraph(req: schemas.SaveParagraphRequest, current_user: dict = Depends(get_current_user)):
    """
    Save paragraph and vocabularies to database
    If vocabularies already exist, reuse existing input_history_id
    """
    try:
        if not req.vocabs or len(req.vocabs) == 0:
            raise HTTPException(status_code=400, detail={
                "error": "missing_vocabularies",
                "message": "At least one vocabulary is required"
            })
            
        if not req.paragraph or req.paragraph.strip() == "":
            raise HTTPException(status_code=400, detail={
                "error": "missing_paragraph",
                "message": "Paragraph content is required"
            })
            
        from app.database.crud import get_input_history_crud, get_saved_paragraph_crud
        from app.database.models import InputHistoryCreateInternal, SavedParagraphCreate
        from bson import ObjectId
        
        input_history_crud = get_input_history_crud()
        saved_paragraph_crud = get_saved_paragraph_crud()
        
        # Get user ID from authenticated user (handle both 'user_id' and 'id' fields)
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token (missing both 'user_id' and 'id' fields)"
            })
        
        # Normalize input vocabularies (lowercase and sorted for comparison)
        input_vocabs = sorted([word.lower().strip() for word in req.vocabs if word.strip()])
        
        if len(input_vocabs) == 0:
            raise HTTPException(status_code=400, detail={
                "error": "invalid_vocabularies",
                "message": "All vocabularies are empty or invalid"
            })
        
        # Check if these exact vocabularies already exist
        existing_input_history = await input_history_crud.find_by_exact_words(user_id, input_vocabs)
        
        if existing_input_history:
            # Use existing input history
            input_history = existing_input_history
            logger.info(f"Reusing existing input history: {input_history.id}")
            message = "Using existing vocabularies, paragraph saved successfully"
        else:
            # Create new input history
            history_data = InputHistoryCreateInternal(
                user_id=user_id,
                words=input_vocabs  # Save normalized vocabs
            )
            
            input_history = await input_history_crud.create_input_history(history_data)
            logger.info(f"Created new input history: {input_history.id}")
            message = "New vocabularies and paragraph saved successfully"
        
        # Create saved paragraph
        paragraph_data = SavedParagraphCreate(
            input_history_id=str(input_history.id),
            paragraph=req.paragraph
        )
        
        saved_paragraph = await saved_paragraph_crud.create_saved_paragraph(paragraph_data)
        logger.info(f"Created saved paragraph: {saved_paragraph.id}")
        
        return schemas.SaveParagraphResponse(
            input_history_id=str(input_history.id),
            saved_paragraph_id=str(saved_paragraph.id),
            message=message,
            status=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error saving paragraph")
        raise HTTPException(status_code=500, detail={
            "error": "paragraph_save_failed",
            "message": "Failed to save paragraph to database",
            "details": str(e)
        })

# === Get all saved paragraphs with vocabularies ===
@router.get("/all-paragraphs")
@router.get("/saved-paragraphs")  # Alias endpoint
async def get_all_paragraphs(limit: int = 100, grouped: bool = True, current_user: dict = Depends(get_current_user)):
    """
    Get all saved paragraphs with their vocabularies
    Available at both /all-paragraphs and /saved-paragraphs
    
    Args:
        limit: Maximum number of results
        grouped: If True, group paragraphs by input_history_id (same vocabularies)
    """
    try:
        from app.database.crud import get_saved_paragraph_crud
        
        saved_paragraph_crud = get_saved_paragraph_crud()
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token (missing both 'user_id' and 'id' fields)"
            })
        
        # Get user's saved paragraphs with input history info
        paragraphs_data = await saved_paragraph_crud.get_user_saved_paragraphs(user_id, limit)
        
        if grouped:
            # Group paragraphs by input_history_id
            grouped_data = {}
            
            for item in paragraphs_data:
                try:
                    input_history_id = str(item['input_history']['_id'])
                    vocabs = item['input_history']['words']
                    paragraph_text = item['paragraph']
                    
                    # Group by input_history_id
                    if input_history_id not in grouped_data:
                        grouped_data[input_history_id] = {
                            "input_history_id": input_history_id,
                            "vocabs": vocabs,
                            "paragraphs": [],
                            "total_paragraphs": 0
                        }
                    
                    # Add paragraph text directly to array
                    grouped_data[input_history_id]["paragraphs"].append(paragraph_text)
                    grouped_data[input_history_id]["total_paragraphs"] += 1
                    
                except Exception as item_error:
                    logger.error(f"Error processing paragraph item: {item_error}")
                    continue
            
            # Convert to list and create response items
            result_groups = []
            for group_data in grouped_data.values():
                # Create group item with simplified structure
                group_item = {
                    "id": group_data["input_history_id"],
                    "vocabs": group_data["vocabs"],
                    "is_group": True,
                    "paragraphs": group_data["paragraphs"],  # Array of paragraph texts
                    "total_paragraphs": group_data["total_paragraphs"]
                }
                result_groups.append(group_item)
            
            return {
                "data": result_groups,
                "total": len(result_groups),
                "status": True
            }
            
        else:
            # Original ungrouped format
            paragraphs = []
            for item in paragraphs_data:
                try:
                    paragraph_item = {
                        "id": str(item['_id']),
                        "vocabs": item['input_history']['words'],
                        "paragraph": item['paragraph'],
                        "created_at": ""  # Not available in aggregation result
                    }
                    paragraphs.append(paragraph_item)
                except Exception as item_error:
                    logger.error(f"Error processing paragraph item: {item_error}")
                    continue
            
            return {
                "data": paragraphs,
                "total": len(paragraphs),
                "status": True
            }
        
    except Exception as e:
        logger.exception("Error getting all paragraphs")
        return {
            "data": [],
            "total": 0,
            "status": False
        }

# === Get paragraphs by input_history_id (group details) ===
@router.get("/paragraphs-by-group/{input_history_id}")
async def get_paragraphs_by_group(input_history_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get all paragraphs for a specific input_history_id (vocabulary group)
    """
    try:
        from app.database.crud import get_saved_paragraph_crud, get_input_history_crud
        from bson import ObjectId
        
        saved_paragraph_crud = get_saved_paragraph_crud()
        input_history_crud = get_input_history_crud()
        
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token (missing both 'user_id' and 'id' fields)"
            })
        
        # Verify that the input_history belongs to the current user
        input_history = await input_history_crud.get_input_history_by_id(input_history_id)
        if not input_history or str(input_history.user_id) != user_id:
            return {
                "status": False,
                "input_history_id": input_history_id,
                "total_paragraphs": 0,
                "paragraphs": [],
                "message": "Input history not found or access denied"
            }
        
        # Get paragraphs by input_history_id
        paragraphs = await saved_paragraph_crud.get_paragraphs_by_input_history(input_history_id)
        
        # Transform to response format
        paragraph_items = []
        for paragraph in paragraphs:
            paragraph_items.append({
                "id": str(paragraph.id),
                "paragraph": paragraph.paragraph,
                "created_at": str(paragraph.created_at) if paragraph.created_at else ""
            })
        
        return {
            "status": True,
            "input_history_id": input_history_id,
            "total_paragraphs": len(paragraph_items),
            "paragraphs": paragraph_items,
            "message": f"Found {len(paragraph_items)} paragraphs for this vocabulary group"
        }
        
    except Exception as e:
        logger.exception("Error getting paragraphs by group")
        return {
            "status": False,
            "input_history_id": input_history_id,
            "total_paragraphs": 0,
            "paragraphs": [],
            "message": f"Failed to get paragraphs: {str(e)}"
        }

# === Get vocabularies by collection ===
@router.get("/vocabs_base_on_category")
async def get_vocabs_by_collection(collection_id: str, sort: str = "newest", current_user: dict = Depends(get_current_user)):
    """
    Get learned vocabularies documents from a specific collection
    Returns complete documents sorted by date, excluding user_id
    
    Args:
        collection_id: ID of the vocabulary collection to filter by (required)
        sort: Sort order - "newest" (default), "oldest", "alphabetical", "frequent"
    """
    try:
        from app.database.crud import get_learned_vocabs_crud, get_vocab_collection_crud
        
        learned_vocabs_crud = get_learned_vocabs_crud()
        vocab_collection_crud = get_vocab_collection_crud()
        
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token (missing both 'user_id' and 'id' fields)"
            })
        
        # Validate collection_id parameter
        if not collection_id or collection_id.strip() == "":
            raise HTTPException(status_code=400, detail={
                "error": "missing_collection_id",
                "message": "collection_id parameter is required"
            })
        
        # Verify collection exists and belongs to the user
        collection = await vocab_collection_crud.get_vocab_collection_by_id(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail={
                "error": "collection_not_found",
                "message": "Vocabulary collection not found"
            })
        
        if str(collection.user_id) != user_id:
            raise HTTPException(status_code=403, detail={
                "error": "access_denied",
                "message": "You can only access your own vocabulary collections"
            })
        
        # Validate sort parameter
        valid_sorts = ["newest", "oldest", "alphabetical", "frequent"]
        if sort not in valid_sorts:
            raise HTTPException(status_code=400, detail={
                "error": "invalid_sort_parameter",
                "message": f"Sort must be one of: {', '.join(valid_sorts)}"
            })
        
        # Get learned vocabs entries for the specific collection
        learned_vocabs_entries = await learned_vocabs_crud.get_vocabs_by_collection(collection_id, limit=1000)
        
        # Format documents for response (exclude user_id, include all fields)
        documents = []
        for entry in learned_vocabs_entries:
            document = {
                "id": str(entry.id),
                "vocab": entry.vocab,  # Changed from vocabs to vocab (single string)
                "collection_id": str(entry.collection_id),
                "usage_count": getattr(entry, 'usage_count', 1),  # Default to 1 if field doesn't exist
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
                "deleted_at": entry.deleted_at.isoformat() if entry.deleted_at else None,
                "is_deleted": entry.is_deleted
            }
            documents.append(document)
        
        # Apply sorting based on sort parameter
        if sort == "newest":
            # Sort by created_at (newest first) - handle None values properly
            documents.sort(key=lambda x: x["created_at"] or "1900-01-01T00:00:00", reverse=True)
        elif sort == "oldest":
            # Sort by created_at (oldest first) - handle None values properly
            documents.sort(key=lambda x: x["created_at"] or "1900-01-01T00:00:00", reverse=False)
        elif sort == "alphabetical":
            # Sort by vocabulary word alphabetically
            documents.sort(key=lambda x: x["vocab"].lower() if x["vocab"] else "zzz")
        elif sort == "frequent":
            # Sort by usage_count (most frequent first), then by created_at (newest first) as tiebreaker
            documents.sort(key=lambda x: (x["usage_count"], x["created_at"] or "1900-01-01T00:00:00"), reverse=True)
        
        return {
            "status": True,
            "collection_id": collection_id,
            "collection_name": collection.name,
            "total_documents": len(documents),
            "documents": documents,
            "sort": documents,  # Put the sorted data array in the sort field
            "sort_method": sort,  # Keep the sort method in a separate field
            "message": f"Found {len(documents)} vocabulary documents in collection '{collection.name}' sorted by {sort}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting vocabulary documents from learned_vocabs by collection")
        return {
            "status": False,
            "collection_id": collection_id if 'collection_id' in locals() else None,
            "total_documents": 0,
            "documents": [],
            "sort": [],  # Empty array for consistency
            "sort_method": sort,
            "message": f"Failed to get vocabulary documents: {str(e)}"
        }

# === Create learned vocabularies ===
@router.post("/learned-vocabs", response_model=schemas.LearnedVocabsBatchResponse)
async def create_learned_vocabs(req: schemas.LearnedVocabsCreateRequest, current_user: dict = Depends(get_current_user)):
    """
    Create new learned vocabularies - one document per vocabulary word
    """
    try:
        # Validate vocabularies
        if not req.vocabs or len(req.vocabs) == 0:
            raise HTTPException(status_code=400, detail={
                "error": "empty_vocabs",
                "message": "At least one vocabulary is required"
            })
        
        # Clean and validate vocabularies
        cleaned_vocabs = []
        for vocab in req.vocabs:
            if isinstance(vocab, str) and vocab.strip():
                cleaned_vocabs.append(vocab.strip())
        
        if len(cleaned_vocabs) == 0:
            raise HTTPException(status_code=400, detail={
                "error": "no_valid_vocabs",
                "message": "No valid vocabularies provided"
            })
        
        from app.database.crud import get_learned_vocabs_crud, get_vocab_collection_crud
        from app.database.models import LearnedVocabsCreateInternal
        
        learned_vocabs_crud = get_learned_vocabs_crud()
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token"
            })
        
        # Validate collection_id (now required)
        vocab_collection_crud = get_vocab_collection_crud()
        collection = await vocab_collection_crud.get_vocab_collection_by_id(req.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail={
                "error": "invalid_collection_id",
                "message": "Vocabulary collection not found"
            })
        
        # Verify collection belongs to current user
        if str(collection.user_id) != user_id:
            raise HTTPException(status_code=403, detail={
                "error": "access_denied",
                "message": "You can only add vocabularies to your own collections"
            })
        
        # Create one document for each vocabulary word
        created_vocabs = []
        for vocab in cleaned_vocabs:
            # Check if this exact vocabulary already exists in this collection
            existing_vocab = await learned_vocabs_crud.find_by_exact_vocab(req.collection_id, vocab)
            
            if existing_vocab:
                # Increment usage count for existing entry
                updated_vocab = await learned_vocabs_crud.increment_usage_count(str(existing_vocab.id))
                logger.info(f"Incremented usage count for learned vocab '{vocab}' ID: {existing_vocab.id}")
                
                created_vocabs.append(schemas.LearnedVocabsResponse(
                    id=str(updated_vocab.id if updated_vocab else existing_vocab.id),
                    vocab=updated_vocab.vocab if updated_vocab else existing_vocab.vocab,
                    collection_id=str(existing_vocab.collection_id),
                    usage_count=updated_vocab.usage_count if updated_vocab else getattr(existing_vocab, 'usage_count', 1),
                    created_at=updated_vocab.created_at.isoformat() if updated_vocab and updated_vocab.created_at else existing_vocab.created_at.isoformat() if existing_vocab.created_at else "",
                    updated_at=updated_vocab.updated_at.isoformat() if updated_vocab and updated_vocab.updated_at else existing_vocab.updated_at.isoformat() if existing_vocab.updated_at else None,
                    is_new=False,
                    usage_incremented=True,
                    status=True
                ))
            else:
                # Create new learned vocab entry
                vocab_create_data = LearnedVocabsCreateInternal(
                    vocab=vocab,
                    collection_id=req.collection_id
                )
                
                learned_vocab = await learned_vocabs_crud.create_learned_vocabs(vocab_create_data)
                logger.info(f"Created new learned vocab '{vocab}' with ID: {learned_vocab.id}")
                
                created_vocabs.append(schemas.LearnedVocabsResponse(
                    id=str(learned_vocab.id),
                    vocab=learned_vocab.vocab,
                    collection_id=str(learned_vocab.collection_id),
                    usage_count=getattr(learned_vocab, 'usage_count', 1),
                    created_at=learned_vocab.created_at.isoformat() if learned_vocab.created_at else "",
                    updated_at=learned_vocab.updated_at.isoformat() if learned_vocab.updated_at else None,
                    is_new=True,
                    usage_incremented=False,
                    status=True
                ))
        
        return schemas.LearnedVocabsBatchResponse(
            created=created_vocabs,
            total_created=len(created_vocabs),
            status=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error creating learned vocabularies")
        raise HTTPException(status_code=500, detail={
            "error": "creation_failed",
            "message": "Failed to create learned vocabularies",
            "details": str(e)
        })

# === Delete vocabulary from learned vocabs ===
@router.delete("/learned-vocabs")
async def delete_vocabulary(req: dict, current_user: dict = Depends(get_current_user)):
    """
    Delete all learned vocabulary entries containing the specified word
    Schema: {"vocab": "word_to_delete"}
    Requires Bearer token authorization
    """
    try:
        # Validate request schema
        if "vocab" not in req:
            raise HTTPException(status_code=400, detail={
                "error": "missing_vocab",
                "message": "Field 'vocab' is required"
            })
        
        vocab = req.get("vocab", "")
        
        if not isinstance(vocab, str):
            raise HTTPException(status_code=400, detail={
                "error": "invalid_vocab_type",
                "message": "Field 'vocab' must be a string"
            })
        
        if not vocab.strip():
            raise HTTPException(status_code=400, detail={
                "error": "empty_vocab",
                "message": "Vocabulary word cannot be empty"
            })
        
        from app.database.crud import get_learned_vocabs_crud
        
        learned_vocabs_crud = get_learned_vocabs_crud()
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token (missing both 'user_id' and 'id' fields)"
            })
        
        # Delete all learned vocabs entries containing the specified word
        deleted_count = await learned_vocabs_crud.delete_vocabs_containing_word(user_id, vocab.strip())
        
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} learned vocabs entries containing word '{vocab}' for user {user_id}")
            return {
                "status": True,
                "message": f"Successfully deleted {deleted_count} vocabulary entries containing '{vocab.strip()}'",
                "deleted_count": deleted_count
            }
        else:
            return {
                "status": False,
                "message": f"No vocabulary entries found containing '{vocab.strip()}'",
                "deleted_count": 0
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting vocabulary")
        raise HTTPException(status_code=500, detail={
            "error": "deletion_failed",
            "message": "Failed to delete vocabulary",
            "details": str(e)
        })

# === Vocab Collections Management ===
@router.post("/vocab-collections", response_model=schemas.VocabCollectionResponse)
async def create_vocab_collection(req: schemas.VocabCollectionCreateRequest, current_user: dict = Depends(get_current_user)):
    """
    Create a new vocabulary collection
    """
    try:
        from app.database.crud import get_vocab_collection_crud
        from app.database.models import VocabCollectionCreate
        
        vocab_collection_crud = get_vocab_collection_crud()
        
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token"
            })
        
        # Create collection with user_id
        collection_data = VocabCollectionCreate(
            name=req.name.strip(),
            user_id=user_id
        )
        collection = await vocab_collection_crud.create_vocab_collection(collection_data)
        
        return schemas.VocabCollectionResponse(
            id=str(collection.id),
            name=collection.name,
            user_id=str(collection.user_id),
            created_at=collection.created_at.isoformat() if collection.created_at else "",
            updated_at=collection.updated_at.isoformat() if collection.updated_at else None,
            status=True
        )
        
    except Exception as e:
        logger.exception("Error creating vocab collection")
        raise HTTPException(status_code=500, detail={
            "error": "creation_failed",
            "message": "Failed to create vocabulary collection",
            "details": str(e)
        })

@router.get("/vocab-collections", response_model=schemas.VocabCollectionsListResponse)
async def get_vocab_collections(current_user: dict = Depends(get_current_user)):
    """
    Get user's vocabulary collections
    """
    try:
        from app.database.crud import get_vocab_collection_crud
        
        vocab_collection_crud = get_vocab_collection_crud()
        
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token"
            })
        
        # Get user's collections only
        collections = await vocab_collection_crud.get_user_vocab_collections(user_id)
        
        collection_responses = []
        for collection in collections:
            collection_responses.append(schemas.VocabCollectionResponse(
                id=str(collection.id),
                name=collection.name,
                user_id=str(collection.user_id),
                created_at=collection.created_at.isoformat() if collection.created_at else "",
                updated_at=collection.updated_at.isoformat() if collection.updated_at else None,
                status=True
            ))
        
        return schemas.VocabCollectionsListResponse(
            collections=collection_responses,
            total=len(collection_responses),
            status=True
        )
        
    except Exception as e:
        logger.exception("Error getting vocab collections")
        raise HTTPException(status_code=500, detail={
            "error": "retrieval_failed",
            "message": "Failed to get vocabulary collections",
            "details": str(e)
        })

@router.put("/vocab-collections/{collection_id}", response_model=schemas.VocabCollectionResponse)
async def update_vocab_collection(collection_id: str, req: schemas.VocabCollectionUpdateRequest, current_user: dict = Depends(get_current_user)):
    """
    Update vocabulary collection name
    """
    try:
        from app.database.crud import get_vocab_collection_crud
        
        vocab_collection_crud = get_vocab_collection_crud()
        collection = await vocab_collection_crud.update_vocab_collection(collection_id, req.name.strip())
        
        if not collection:
            raise HTTPException(status_code=404, detail={
                "error": "collection_not_found",
                "message": "Vocabulary collection not found"
            })
        
        return schemas.VocabCollectionResponse(
            id=str(collection.id),
            name=collection.name,
            created_at=collection.created_at.isoformat() if collection.created_at else "",
            updated_at=collection.updated_at.isoformat() if collection.updated_at else None,
            status=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error updating vocab collection")
        raise HTTPException(status_code=500, detail={
            "error": "update_failed",
            "message": "Failed to update vocabulary collection",
            "details": str(e)
        })

@router.delete("/vocab-collections/{collection_id}")
async def delete_vocab_collection(collection_id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete vocabulary collection with cascade deletion of associated learned vocabularies
    Also updates user's selected_collection_id if it points to the deleted collection
    """
    try:
        from app.database.crud import get_vocab_collection_crud, get_learned_vocabs_crud
        from bson import ObjectId
        
        vocab_collection_crud = get_vocab_collection_crud()
        learned_vocabs_crud = get_learned_vocabs_crud()
        user_crud = get_user_crud()
        
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token"
            })
        
        # Verify the collection exists and belongs to the user
        collection = await vocab_collection_crud.get_vocab_collection_by_id(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail={
                "error": "collection_not_found",
                "message": "Vocabulary collection not found"
            })
        
        if str(collection.user_id) != user_id:
            raise HTTPException(status_code=403, detail={
                "error": "access_denied",
                "message": "You can only delete your own vocabulary collections"
            })
        
        # Get count of vocabularies before deletion for response
        vocabs_in_collection = await learned_vocabs_crud.get_vocabs_by_collection(collection_id, limit=10000)
        vocab_count = len(vocabs_in_collection)
        
        # Perform cascade deletion (collection + all associated learned_vocabs)
        success = await vocab_collection_crud.delete_vocab_collection(collection_id)
        
        if not success:
            raise HTTPException(status_code=500, detail={
                "error": "deletion_failed",
                "message": "Failed to delete vocabulary collection"
            })
        
        # Check if user's selected_collection_id points to the deleted collection
        user_db = await user_crud.get_user_by_id(user_id)
        if user_db and user_db.selected_collection_id == collection_id:
            # Get user's remaining collections
            remaining_collections = await vocab_collection_crud.get_user_vocab_collections(user_id)
            
            if remaining_collections:
                # Set selected_collection_id to the first remaining collection
                new_selected_id = str(remaining_collections[0].id)
                await user_crud.collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"selected_collection_id": new_selected_id}}
                )
                logger.info(f"✅ Updated user's selected_collection_id to: {new_selected_id}")
            else:
                # No collections left, set to None
                await user_crud.collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"selected_collection_id": None}}
                )
                logger.info(f"✅ User has no more collections, set selected_collection_id to None")
        
        logger.info(f"✅ Deleted collection '{collection.name}' and {vocab_count} associated vocabularies")
        
        return {
            "status": True,
            "message": f"Vocabulary collection deleted successfully (including {vocab_count} vocabularies)",
            "deleted_vocab_count": vocab_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting vocab collection")
        raise HTTPException(status_code=500, detail={
            "error": "deletion_failed",
            "message": "Failed to delete vocabulary collection",
            "details": str(e)
        })

# === Study History Management ===
@router.post("/study-session", response_model=schemas.StudySessionResponse)
async def record_study_session(req: schemas.StudySessionRequest, current_user: dict = Depends(get_current_user)):
    """
    Record a study session for a vocabulary
    """
    try:
        from app.database.crud import get_history_by_date_crud, get_learned_vocabs_crud
        from datetime import datetime
        
        history_crud = get_history_by_date_crud()
        vocabs_crud = get_learned_vocabs_crud()
        
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token"
            })
        
        # Verify vocab belongs to user
        vocab = await vocabs_crud.get_learned_vocabs_by_id(req.vocab_id)
        if not vocab or str(vocab.user_id) != user_id:
            raise HTTPException(status_code=404, detail={
                "error": "vocab_not_found",
                "message": "Vocabulary not found or access denied"
            })
        
        # Parse study date or use current date
        if req.study_date:
            try:
                # Try parsing as full datetime first
                if 'T' in req.study_date or 'Z' in req.study_date:
                    study_date = datetime.fromisoformat(req.study_date.replace('Z', '+00:00'))
                else:
                    # Parse as date-only (YYYY-MM-DD)
                    from datetime import date
                    date_obj = datetime.strptime(req.study_date, '%Y-%m-%d').date()
                    study_date = datetime.combine(date_obj, datetime.min.time())
            except ValueError:
                raise HTTPException(status_code=400, detail={
                    "error": "invalid_date_format",
                    "message": "study_date must be in YYYY-MM-DD or ISO datetime format"
                })
        else:
            # Use current date (without time)
            today = datetime.utcnow().date()
            study_date = datetime.combine(today, datetime.min.time())
        
        # Record study session
        history = await history_crud.increment_study_count(req.vocab_id, study_date)
        
        return schemas.StudySessionResponse(
            id=str(history.id),
            vocab_id=str(history.vocab_id),
            study_date=history.study_date.strftime('%Y-%m-%d'),  # Return as date-only string
            count=history.count,
            created_at=history.created_at.isoformat() if history.created_at else "",
            status=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error recording study session")
        raise HTTPException(status_code=500, detail={
            "error": "recording_failed",
            "message": "Failed to record study session",
            "details": str(e)
        })

@router.get("/study-history", response_model=schemas.StudyHistoryResponse)
async def get_study_history(limit: int = 50, current_user: dict = Depends(get_current_user)):
    """
    Get user's study history
    """
    try:
        from app.database.crud import get_history_by_date_crud
        
        history_crud = get_history_by_date_crud()
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token"
            })
        
        # Get study history with vocab info
        history_data = await history_crud.get_user_study_history(user_id, limit)
        
        # Format response
        formatted_history = []
        for item in history_data:
            formatted_item = {
                "id": str(item["_id"]),
                "vocab_id": str(item["vocab_id"]),
                "study_date": item["study_date"].strftime('%Y-%m-%d'),  # Return as date-only string
                "count": item["count"],
                "created_at": item["created_at"].isoformat() if item.get("created_at") else "",
                "vocab_info": {
                    "id": str(item["vocab_info"]["_id"]),
                    "vocabs": item["vocab_info"]["vocabs"],
                    "collection_id": str(item["vocab_info"]["collection_id"]) if item["vocab_info"].get("collection_id") else None,
                    "usage_count": item["vocab_info"].get("usage_count", 1)
                }
            }
            formatted_history.append(formatted_item)
        
        return schemas.StudyHistoryResponse(
            history=formatted_history,
            total=len(formatted_history),
            status=True
        )
        
    except Exception as e:
        logger.exception("Error getting study history")
        raise HTTPException(status_code=500, detail={
            "error": "retrieval_failed",
            "message": "Failed to get study history",
            "details": str(e)
        })

# === User Feedback ===
@router.post("/feedback", response_model=schemas.UserFeedbackResponse)
async def submit_feedback(req: schemas.UserFeedbackRequest):
    """
    Submit user feedback (no authentication required)
    """
    try:
        from app.database.crud import get_user_feedback_crud
        from app.database.models import UserFeedbackCreate
        
        feedback_crud = get_user_feedback_crud()
        
        # Create feedback
        feedback_data = UserFeedbackCreate(
            email=req.email,
            name=req.name,
            message=req.message
        )
        feedback = await feedback_crud.create_feedback(feedback_data)
        
        logger.info(f"📝 New feedback received from {req.email}")
        
        return schemas.UserFeedbackResponse(
            id=str(feedback.id),
            email=feedback.email,
            name=feedback.name,
            message=feedback.message,
            created_at=feedback.created_at.isoformat() if feedback.created_at else "",
            status=True
        )
        
    except Exception as e:
        logger.exception("Error submitting feedback")
        raise HTTPException(status_code=500, detail={
            "error": "submission_failed",
            "message": "Failed to submit feedback",
            "details": str(e)
        })

@router.get("/feedback", response_model=schemas.UserFeedbackListResponse)
async def get_all_feedback(limit: int = 100, current_user: dict = Depends(get_current_user)):
    """
    Get all feedback (admin only - requires authentication)
    """
    try:
        from app.database.crud import get_user_feedback_crud
        
        feedback_crud = get_user_feedback_crud()
        feedbacks = await feedback_crud.get_all_feedback(limit)
        
        feedback_responses = []
        for feedback in feedbacks:
            feedback_responses.append(schemas.UserFeedbackResponse(
                id=str(feedback.id),
                email=feedback.email,
                name=feedback.name,
                message=feedback.message,
                created_at=feedback.created_at.isoformat() if feedback.created_at else "",
                status=True
            ))
        
        return schemas.UserFeedbackListResponse(
            feedbacks=feedback_responses,
            total=len(feedback_responses),
            status=True
        )
        
    except Exception as e:
        logger.exception("Error getting feedback")
        raise HTTPException(status_code=500, detail={
            "error": "retrieval_failed",
            "message": "Failed to get feedback",
            "details": str(e)
        })

# === Streak Management ===
@router.post("/streak", response_model=schemas.StreakResponse)
async def create_streak(req: schemas.StreakCreateRequest, current_user: dict = Depends(get_current_user)):
    """
    Create or update a streak entry for the current user
    """
    try:
        from app.database.crud import get_streak_crud
        from app.database.models import StreakCreateInternal, StreakCreate
        from datetime import datetime
        
        streak_crud = get_streak_crud()
        
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token"
            })
        
        # Parse learned_date or use current date
        if req.learned_date:
            try:
                # Try parsing as full datetime first
                if 'T' in req.learned_date or 'Z' in req.learned_date:
                    learned_date = datetime.fromisoformat(req.learned_date.replace('Z', '+00:00'))
                else:
                    # Parse as date-only (YYYY-MM-DD)
                    from datetime import date
                    date_obj = datetime.strptime(req.learned_date, '%Y-%m-%d').date()
                    learned_date = datetime.combine(date_obj, datetime.min.time())
            except ValueError:
                raise HTTPException(status_code=400, detail={
                    "error": "invalid_date_format",
                    "message": "learned_date must be in YYYY-MM-DD or ISO datetime format"
                })
        else:
            # Use current date (without time)
            today = datetime.utcnow().date()
            learned_date = datetime.combine(today, datetime.min.time())
        
        # Create streak entry
        streak_data = StreakCreateInternal(
            user_id=user_id,
            learned_date=learned_date
        )
        
        streak = await streak_crud.create_streak(streak_data)
        
        logger.info(f"📈 Streak recorded for user {user_id} on {learned_date.strftime('%Y-%m-%d')}: count={streak.count}, is_qualify={streak.is_qualify}")
        
        return schemas.StreakResponse(
            id=str(streak.id),
            user_id=str(streak.user_id),
            learned_date=streak.learned_date.strftime('%Y-%m-%d'),
            count=streak.count,
            is_qualify=streak.is_qualify,
            created_at=streak.created_at.isoformat() if streak.created_at else "",
            status=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error creating streak")
        raise HTTPException(status_code=500, detail={
            "error": "creation_failed",
            "message": "Failed to create streak",
            "details": str(e)
        })

@router.get("/streak-chain", response_model=schemas.StreakChainResponse)
async def get_streak_chain(startday: str, endday: str, current_user: dict = Depends(get_current_user)):
    """
    Get streak chain for a date range
    
    Args:
        startday: Start date in YYYY-MM-DD format
        endday: End date in YYYY-MM-DD format
    """
    try:
        from app.database.crud import get_streak_crud
        from datetime import datetime, timedelta
        
        streak_crud = get_streak_crud()
        
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token"
            })
        
        # Parse dates
        try:
            start_date = datetime.strptime(startday, '%Y-%m-%d')
            end_date = datetime.strptime(endday, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail={
                "error": "invalid_date_format",
                "message": "Dates must be in YYYY-MM-DD format"
            })
        
        # Validate date range
        if start_date > end_date:
            raise HTTPException(status_code=400, detail={
                "error": "invalid_date_range",
                "message": "start_date must be before or equal to end_date"
            })
        
        # Get streak data for the date range
        streaks = await streak_crud.get_streak_by_date_range(user_id, start_date, end_date)
        
        # Create a map of dates to streak data for fast lookup
        streak_map = {
            streak.learned_date.strftime('%Y-%m-%d'): streak 
            for streak in streaks
        }
        
        # Generate all dates in the range
        dates_list = []
        current_date = start_date
        completed_days = 0
        qualified_days = 0
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            streak_data = streak_map.get(date_str)
            is_completed = streak_data is not None
            
            dates_list.append(schemas.DateCompletionStatus(
                date=date_str,
                completed=is_completed,
                count=streak_data.count if streak_data else None,
                is_qualify=streak_data.is_qualify if streak_data else False
            ))
            
            if is_completed:
                completed_days += 1
            
            if streak_data and streak_data.is_qualify:
                qualified_days += 1
            
            current_date += timedelta(days=1)
        
        total_days = len(dates_list)
        
        return schemas.StreakChainResponse(
            id=hash(f"{user_id}_{startday}_{endday}") % (10 ** 8),  # Generate a pseudo-unique ID
            start_date=startday,
            end_date=endday,
            dates=dates_list,
            total_days=total_days,
            completed_days=completed_days,
            qualified_days=qualified_days,
            status=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting streak chain")
        raise HTTPException(status_code=500, detail={
            "error": "retrieval_failed",
            "message": "Failed to get streak chain",
            "details": str(e)
        })

@router.get("/today-yesterday-streak-status", response_model=schemas.TodayStreakStatusResponse)
async def get_today_yesterday_streak_status(date: str = "today", current_user: dict = Depends(get_current_user)):
    """
    Get streak status for today or yesterday (count, is_qualify, and date)
    
    Args:
        date: Either "today" (default) or "yesterday"
    
    If no data exists, returns:
    {
        "count": 0,
        "is_qualify": false,
        "date": "2025-10-13",
        "status": true
    }
    """
    try:
        from app.database.crud import get_streak_crud
        from datetime import datetime, timedelta
        
        streak_crud = get_streak_crud()
        
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token"
            })
        
        # Validate date parameter
        if date not in ["today", "yesterday"]:
            raise HTTPException(status_code=400, detail={
                "error": "invalid_date_parameter",
                "message": "Parameter 'date' must be either 'today' or 'yesterday'"
            })
        
        # Get target date based on parameter
        today = datetime.utcnow().date()
        if date == "yesterday":
            target_date = today - timedelta(days=1)
        else:  # date == "today"
            target_date = today
        
        target_datetime = datetime.combine(target_date, datetime.min.time())
        target_date_str = target_date.strftime('%Y-%m-%d')
        
        # Get streak data for the target date
        streak_data = await streak_crud.get_streak_by_user_and_date(user_id, target_datetime)
        
        if streak_data:
            # Return existing data
            return schemas.TodayStreakStatusResponse(
                count=streak_data.count or 0,
                is_qualify=streak_data.is_qualify,
                date=target_date_str,
                status=True
            )
        else:
            # No data for target date, return default values
            return schemas.TodayStreakStatusResponse(
                count=0,
                is_qualify=False,
                date=target_date_str,
                status=True
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting streak status for {date}")
        raise HTTPException(status_code=500, detail={
            "error": "retrieval_failed",
            "message": f"Failed to get streak status for {date}",
            "details": str(e)
        })

# === Simple test endpoint ===
@router.get("/test-data")
async def get_test_data():
    """Simple test endpoint to verify API is working"""
    return {
        "message": "API is working",
        "data": [
            {"id": "1", "vocabs": ["hello", "world"], "paragraph": "Hello world example"},
            {"id": "2", "vocabs": ["python", "code"], "paragraph": "Python code example"}
        ],
        "total": 2,
        "status": True
    }
