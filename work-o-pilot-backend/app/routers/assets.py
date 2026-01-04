from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
import uuid
from app.services.supabase_client import supabase

router = APIRouter(prefix="/assets", tags=["assets"])

class AssetCreate(BaseModel):
    user_id: uuid.UUID
    symbol: str
    quantity: float
    avg_buy_price: float
    purchase_date: Optional[date] = None
    portfolio_name: Optional[str] = None
    currency: str = "USD"
    broker: Optional[str] = None
    investment_type: str = "Stock"
    additional_info: Optional[str] = None
    exchange: Optional[str] = None


@router.get("/{user_id}")
async def get_user_assets(user_id: uuid.UUID):
    """
    Get all assets for a user.
    
    Returns list of assets with current market data.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        response = supabase.table("assets").select("*").eq(
            "user_id", str(user_id)
        ).execute()
        
        return {
            "user_id": str(user_id),
            "count": len(response.data),
            "assets": response.data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{user_id}/{symbol}")
async def get_asset_by_symbol(user_id: uuid.UUID, symbol: str):
    """
    Get a specific asset by symbol for a user.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        response = supabase.table("assets").select("*").eq(
            "user_id", str(user_id)
        ).eq("symbol", symbol.upper()).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {symbol} not found for user"
            )
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{user_id}/{symbol}")
async def delete_asset(user_id: uuid.UUID, symbol: str):
    """
    Delete an asset by symbol for a user.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        response = supabase.table("assets").delete().eq(
            "user_id", str(user_id)
        ).eq("symbol", symbol.upper()).execute()
        
        return {"success": True, "deleted": symbol.upper()}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_asset(
    user_id: uuid.UUID = Form(...),
    symbol: str = Form(...),
    quantity: float = Form(...),
    avg_buy_price: float = Form(...),
    purchase_date: Optional[date] = Form(None),
    portfolio_name: Optional[str] = Form(None),
    currency: str = Form("USD"),
    broker: Optional[str] = Form(None),
    investment_type: str = Form("Stock"),
    additional_info: Optional[str] = Form(None),
    exchange: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[])
):
    """
    Create a new asset for a user.
    
    Accepts form data and optional file uploads.
    """
    if not supabase:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Supabase client not initialized")

    print("Called Assets")
    structured_file_urls = []
    unstructured_file_urls = []

    for file in files:
        file_content = await file.read()
        file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        
        bucket_name = "unstructured_files"
        if file_ext in ["csv", "xls", "xlsx"]:
            bucket_name = "structured_files"
        
        file_path = f"{user_id}/{uuid.uuid4()}.{file_ext}"
        
        try:
            supabase.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": file.content_type}
            )
            
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            
            if bucket_name == "structured_files":
                structured_file_urls.append(public_url)
            else:
                unstructured_file_urls.append(public_url)
                
        except Exception as e:
            print(f"Failed to upload {file.filename}: {e}")

    asset_data = {
        "user_id": str(user_id),
        "symbol": symbol.upper(),
        "quantity": quantity,
        "avg_buy_price": avg_buy_price,
        "purchase_date": purchase_date.isoformat() if purchase_date else None,
        "portfolio_name": portfolio_name,
        "currency": currency,
        "broker": broker,
        "investment_type": investment_type,
        "additional_info": additional_info,
        "exchange": exchange,
        "structured_file_urls": structured_file_urls,
        "unstructured_file_urls": unstructured_file_urls
    }

    try:
        response = supabase.table("assets").insert(asset_data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

