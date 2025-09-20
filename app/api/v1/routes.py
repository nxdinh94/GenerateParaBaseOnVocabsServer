from fastapi import APIRouter, HTTPException, Depends, Header
from app.api.v1 import schemas
from app.api.v1.database_routes import router as db_router
from app.services.openai_client import OpenAIClient
from app.services.gemini_client import GeminiClient
from app.services.google_auth import google_auth_service
from app.database.crud import get_user_crud, get_refresh_token_crud
from app.database.models import GoogleUserCreate, RefreshTokenCreate
from app.utils.logging_conf import get_logger
from typing import Optional

logger = get_logger("routes")
router = APIRouter(prefix="/api/v1", tags=["v1"])

# Include database routes
router.include_router(db_router)

gemini_client = GeminiClient()
openai_client = OpenAIClient()

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
        
        # Create JWT token for our application (using database user ID)
        jwt_user_data = {
            "id": str(user_db.id),  # Use database user ID (_id) as primary identifier
            "user_id": str(user_db.id),  # Keep for backward compatibility
            "google_id": user_db.google_id,  # Store Google ID for reference
            "email": user_db.email,
            "name": user_db.name,
            "picture": user_db.picture,
            "verified_email": user_db.verified_email
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
        
        # Create new JWT token with same user data
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
                "picture": user_data.get("picture")
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

# === Generic text generation ===
@router.post("/generate", response_model=schemas.GenerateResponse)
async def generate_text(req: schemas.GenerateRequest):
    try:
        res_text = await gemini_client.generate_text(req.prompt, req.max_tokens or 256)
        return schemas.GenerateResponse(result=res_text, status=True)
    except Exception as e:
        logger.exception("Error calling Gemini")
        raise HTTPException(status_code=500, detail=str(e))


# === Paragraph with vocabularies ===
@router.post("/generate-paragraph", response_model=schemas.ParagraphResponse)
async def generate_paragraph(req: schemas.ParagraphRequest):
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
        base_prompt = (
            f"Write only one {"sentence" if paragraphLength == 1 else "paragraph with {paragraphLength} in length"} in {req.language} "
            f"at {req.level} level with a {req.tone} tone and {"beginner" if req.topic == '' else req.topic} topic. The paragraph must include these vocabularies: "
            f"{', '.join(req.vocabularies)}. Make sure to use all the vocabularies at least once."
            f"Highlight the vocabularies in bold in the paragraph."
            f"Also list all the meaning of this vocabs base on Cambridge indeed, give example for each meaning."
            f"Finally, explain the meaning of the vocabularies in the paragraph, which meanings is use in the paragraph."
            f"always return data following json format:"
            f"{
                { 
                    "paragraph": "", 
                    "explain_vocabs": { 
                        "vocabulary_1": [ 
                            {
                                "phonetic_transcription": "",
                                "part_of_speech": "",
                            },
                            { 
                                "meaning": "", 
                                "example": "",
                               
                            }, 
                           { 
                                "meaning": "", 
                                "example": "",
                            }, 
                    
                        ],
                        "vocabulary_2": [ 
                            { 
                                "meaning": "", 
                                "example": "",
                            }, 
                        ]
                    }, 
                    "explanation_in_paragraph": {
                        "vocabulary_1": "explanation of meaning used in paragraph, hightlight the vocabularies in bold",
                        "vocabulary_2": "explanation of meaning used in paragraph, hightlight the vocabularies in bold"
                    }
                }}"
            )
        if req.prompt:
            final_prompt = f"{base_prompt}\nAdditional instruction: {req.prompt}"
        else:
            final_prompt = base_prompt

        res_text = await gemini_client.generate_text(final_prompt)
        # res_text = await gemini_client.generate_text(final_prompt)
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

# === Get all unique vocabularies ===
@router.get("/unique-vocabs")
async def get_unique_vocabs(sort: str = "newest", current_user: dict = Depends(get_current_user)):
    """
    Get all learned vocabularies documents from learned_vocabs collection
    Returns complete documents sorted by date, excluding user_id
    
    Args:
        sort: Sort order - "newest" (default), "oldest", "alphabetical", "frequent"
    """
    try:
        from app.database.crud import get_learned_vocabs_crud
        
        learned_vocabs_crud = get_learned_vocabs_crud()
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token (missing both 'user_id' and 'id' fields)"
            })
        
        # Validate sort parameter
        valid_sorts = ["newest", "oldest", "alphabetical", "frequent"]
        if sort not in valid_sorts:
            raise HTTPException(status_code=400, detail={
                "error": "invalid_sort_parameter",
                "message": f"Sort must be one of: {', '.join(valid_sorts)}"
            })
        
        # Get all learned vocabs entries for the user (always get newest first from DB)
        learned_vocabs_entries = await learned_vocabs_crud.get_user_learned_vocabs(user_id, limit=1000)
        
        # Format documents for response (exclude user_id, include all fields)
        documents = []
        for entry in learned_vocabs_entries:
            document = {
                "id": str(entry.id),
                "vocabs": entry.vocabs,
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
            # Sort by first vocabulary word alphabetically
            documents.sort(key=lambda x: x["vocabs"][0].lower() if x["vocabs"] else "zzz")
        elif sort == "frequent":
            # Sort by usage_count (most frequent first), then by created_at (newest first) as tiebreaker
            documents.sort(key=lambda x: (x["usage_count"], x["created_at"] or "1900-01-01T00:00:00"), reverse=True)
        
        return {
            "status": True,
            "total_documents": len(documents),
            "documents": documents,
            "sort": documents,  # Put the sorted data array in the sort field
            "sort_method": sort,  # Keep the sort method in a separate field
            "message": f"Found {len(documents)} vocabulary documents sorted by {sort}"
        }
        
    except Exception as e:
        logger.exception("Error getting vocabulary documents from learned_vocabs")
        return {
            "status": False,
            "total_documents": 0,
            "documents": [],
            "sort": [],  # Empty array for consistency
            "sort_method": sort,
            "message": f"Failed to get vocabulary documents: {str(e)}"
        }

# === Create learned vocabularies ===
@router.post("/learned-vocabs")
async def create_learned_vocabs(req: dict, current_user: dict = Depends(get_current_user)):
    """
    Create new learned vocabularies entry
    Schema: {"vocabs": ["word1", "word2", "word3"]}
    Requires Bearer token authorization
    """
    try:
        # Validate request schema
        if "vocabs" not in req:
            raise HTTPException(status_code=400, detail={
                "error": "missing_vocabs",
                "message": "Field 'vocabs' is required"
            })
        
        vocabs = req.get("vocabs", [])
        
        if not isinstance(vocabs, list):
            raise HTTPException(status_code=400, detail={
                "error": "invalid_vocabs_type",
                "message": "Field 'vocabs' must be an array"
            })
        
        if len(vocabs) == 0:
            raise HTTPException(status_code=400, detail={
                "error": "empty_vocabs",
                "message": "At least one vocabulary is required"
            })
        
        # Clean and validate vocabularies
        cleaned_vocabs = []
        for vocab in vocabs:
            if isinstance(vocab, str) and vocab.strip():
                cleaned_vocabs.append(vocab.strip())
        
        if len(cleaned_vocabs) == 0:
            raise HTTPException(status_code=400, detail={
                "error": "no_valid_vocabs",
                "message": "No valid vocabularies provided"
            })
        
        from app.database.crud import get_learned_vocabs_crud
        from app.database.models import LearnedVocabsCreateInternal
        
        learned_vocabs_crud = get_learned_vocabs_crud()
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail={
                "error": "invalid_user_data",
                "message": "User ID not found in token (missing both 'user_id' and 'id' fields)"
            })
        
        # Check if these exact vocabularies already exist
        existing_vocabs = await learned_vocabs_crud.find_by_exact_vocabs(user_id, cleaned_vocabs)
        
        if existing_vocabs:
            # Increment usage count for existing entry
            updated_vocabs = await learned_vocabs_crud.increment_usage_count(str(existing_vocabs.id))
            logger.info(f"Incremented usage count for learned vocabs ID: {existing_vocabs.id}, new count: {updated_vocabs.usage_count if updated_vocabs else 'unknown'}")
            
            # Return updated entry
            return {
                "status": True,
                "message": "Vocabularies already exist, usage count incremented",
                "data": {
                    "id": str(updated_vocabs.id if updated_vocabs else existing_vocabs.id),
                    "vocabs": updated_vocabs.vocabs if updated_vocabs else existing_vocabs.vocabs,
                    "usage_count": updated_vocabs.usage_count if updated_vocabs else getattr(existing_vocabs, 'usage_count', 1),
                    "created_at": updated_vocabs.created_at.isoformat() if updated_vocabs and updated_vocabs.created_at else existing_vocabs.created_at.isoformat() if existing_vocabs.created_at else None,
                    "updated_at": updated_vocabs.updated_at.isoformat() if updated_vocabs and updated_vocabs.updated_at else existing_vocabs.updated_at.isoformat() if existing_vocabs.updated_at else None,
                    "deleted_at": updated_vocabs.deleted_at.isoformat() if updated_vocabs and updated_vocabs.deleted_at else existing_vocabs.deleted_at.isoformat() if existing_vocabs.deleted_at else None,
                    "is_deleted": updated_vocabs.is_deleted if updated_vocabs else existing_vocabs.is_deleted
                },
                "is_new": False,
                "usage_incremented": True
            }
        
        # Create new learned vocabs entry
        vocabs_create_data = LearnedVocabsCreateInternal(
            user_id=user_id,
            vocabs=cleaned_vocabs
        )
        
        learned_vocabs = await learned_vocabs_crud.create_learned_vocabs(vocabs_create_data)
        logger.info(f"Created new learned vocabs with ID: {learned_vocabs.id}")
        
        return {
            "status": True,
            "message": "Learned vocabularies created successfully",
            "data": {
                "id": str(learned_vocabs.id),
                "vocabs": learned_vocabs.vocabs,
                "usage_count": getattr(learned_vocabs, 'usage_count', 1),
                "created_at": learned_vocabs.created_at.isoformat() if learned_vocabs.created_at else None,
                "updated_at": learned_vocabs.updated_at.isoformat() if learned_vocabs.updated_at else None,
                "deleted_at": learned_vocabs.deleted_at.isoformat() if learned_vocabs.deleted_at else None,
                "is_deleted": learned_vocabs.is_deleted
            },
            "is_new": True,
            "usage_incremented": False
        }
        
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
