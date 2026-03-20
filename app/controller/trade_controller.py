from fastapi import APIRouter, HTTPException, Depends, Query, Request, Header
from app.service.trade_service import TradeService
from app.models.user import User
from app.db.session import get_db
from app.dto.trade_request import Traderequestdto
from app.dto.trade_response import Traderesponsedto
from app.dto.cancel_order_request import CancelOrderRequestDto
from app.dto.modify_order_request import ModifyOrderRequestDto , ModifyOrderActionDTO
from app.dto.order_action_response import OrderActionResponseDto
from app.dto.smart_order_request import GTTOrderRequestDTO , OCORequestDTO,ModifyGTTRequestDTO, ModifyGTTActionDTO, ModifyOCORequestDTO, ModifyOCOActionDTO, CancelSmartOrderRequestDTO
from app.utils.json_sanitizer import sanitize_for_json
from app.utils.exceptions import TradeException
from sqlalchemy.orm import Session
from app.dto.bulk_order_request import BulkCancelRequestDTO, BulkModifyActionRequestDTO, BulkModifyRequestDTO
from app.dto.ui_order_request import UIOrderRequestDTO



router = APIRouter(prefix="/api/trade", tags=["Trading"])

def get_current_user(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)    
) -> User:
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise Exception("Invalid user")
    return user

def get_trade_service(
        request: Request,
        user: User = Depends(get_current_user)
):
    return TradeService(user, request.app.state.ws_manager)

@router.post("/buy")
def buy_trade(
    request: Traderequestdto,
    service: TradeService = Depends(get_trade_service)
):
    result = service.buy(
        symbol=request.symbol,
        quantity=request.quantity,
        segment=request.segment,
        product=request.product,
        order_type=request.order_type,
        price=request.price,
        trigger_price=request.trigger_price,
        validity=request.validity,
        exchange=request.exchange,
        order_reference_id=request.order_reference_id
    )

    if not result["success"]:
        return {
           "status": "FAILED",
           "reason": result.get("reason" ,"Order Failed")
        }
    
    return {
        "status": "SUCCESS",
        "order_id": result["order_id"]
    }


@router.post("/ui/limit-buy")
def place_limit_buy_ui(
    request: UIOrderRequestDTO,
    service: TradeService = Depends(get_trade_service)
):
    result = service.place_limit_buy_from_ui(request)

    if not result["success"]:
        return {
            "status": "FAILED",
            "reason": result.get("reason", "Order Failed")
        }

    return {
        "status": "SUCCESS",
        "data": result["data"]
    }



@router.post("/sell")
def sell_trade(
    request: Traderequestdto,
    service: TradeService = Depends(get_trade_service)
):
    result = service.sell(
        symbol=request.symbol,
        quantity=request.quantity,
        segment=request.segment,
        product=request.product,
        order_type=request.order_type,
        price=request.price,
        trigger_price=request.trigger_price,
        validity=request.validity,
        exchange=request.exchange,
        order_reference_id=request.order_reference_id
    )

    if not result["success"]:
        return {
            "status": "FAILED",
            "reason": result.get("reason", "Sell Order Failed")
        }

    return {
        "status": "SUCCESS",
        "order_id": result["order_id"]
    }


@router.post("/cancel")
def cancel_trade(
    request: CancelOrderRequestDto,
    service: TradeService = Depends(get_trade_service)
):
    try:
        result = service.cancel(request.order_id, request.segment)

        print("CANCEL RESPONSE:", result)

        return {
            "status": "SUCCESS",
            "order_id": result.get("groww_order_id"),
            "broker_status": result.get("order_status")
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.post("/cancel",response_model=OrderActionResponseDto)
# def cancel_trade(
#     request: CancelOrderRequestDto,
#     service: TradeService = Depends(get_trade_service)
# ):
#     try:
#         result = service.cancel(request.order_id, request.segment)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    


@router.post("/bulk/cancel")
def bulk_cancel(
    request: BulkCancelRequestDTO,
    service: TradeService = Depends(get_trade_service)
):
    try:
        return service.bulk_cancel_by_symbol(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


@router.put("/bulk/modify-action")
def bulk_modify_action(
    request: BulkModifyActionRequestDTO,
    service: TradeService = Depends(get_trade_service)
):
    try:
        return service.bulk_modify_with_action_by_symbol(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/modify")
def modify_trade(
    request: ModifyOrderRequestDto,
    service: TradeService = Depends(get_trade_service)
):
    try:
        result = service.modify(
            order_id=request.order_id,
            quantity=request.quantity,
            segment=request.segment,
            order_type=request.order_type,
            price=request.price,
            trigger_price=request.trigger_price
        )

        print("MODIFY RESPONSE:", result)

        return {
            "status": "SUCCESS",
            "groww_order_id": result.get("groww_order_id"),
            "broker_status": result.get("order_status")
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/bulk/modify")
def bulk_modify(
    request: BulkModifyRequestDTO,
    service: TradeService = Depends(get_trade_service)
):

    try:
        return service.bulk_modify_by_symbol(request)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# @router.post("/modify", response_model=OrderActionResponseDto)
# def modify_trade(
#     request: ModifyOrderRequestDto,
#     service: TradeService = Depends(get_trade_service)
# ):
#     try:
#         result=service.modify(
#             order_id=request.order_id,
#             quantity=request.quantity,
#             segment=request.segment,
#             order_type=request.order_type,
#             price=request.price,
#             trigger_price=request.trigger_price
#         )

#         return {
#             "status": "SUCCESS",
#             "order_id": result.get("groww_order_id")
#         }
    
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


@router.put("/modify-action")
def modify_trade_action(
    request: ModifyOrderActionDTO,
    service: TradeService = Depends(get_trade_service)
):
    try:
        return service.modify_with_action(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    

@router.get("tradelist")
def get_tradelist_for_order(
    groww_order_id:str=Query(..., example="GMK39038RDT490CCVRO"),
    segment:str=Query(..., example="CASH"),
    page:int=Query(..., example="0"),
    page_size:int=Query(..., example="50"),
    service: TradeService = Depends(get_trade_service) 
):
    try:
        result = service.get_tradelist_for_orders(groww_order_id,segment,page,page_size)
        clean_result = sanitize_for_json(result)

        return{
            "status": "success",
            "trade_list": clean_result
        }
    
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/order_status")
def get_order_status(
    groww_order_id:str=Query(..., example="GMK39038RDT490CCVRO"),
    segment:str=Query(..., example="CASH"),
    service: TradeService = Depends(get_trade_service) 
):
    try:
        result = service.get_order_status(groww_order_id,segment)
        clean_result = sanitize_for_json(result)

        return{
            "status": "success",
            "order_status": clean_result
        }
    
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/order_status_by_reference")
def get_order_status_by_reference(
    order_reference_id :str=Query(..., example="Ab-654321234-1628190"),
    segment:str=Query(..., example="CASH"),
    service: TradeService = Depends(get_trade_service) 
):
    try:
        result = service.get_order_status_by_reference(order_reference_id,segment)
        clean_result = sanitize_for_json(result)

        return{
            "status": "success",
            "order_status": clean_result
        }
    
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/orderlist")
def get_order_list(
    segment:str=Query(..., example="CASH"),
    page:int=Query(..., example="0"),
    page_size:int=Query(..., example="100"),
    service: TradeService = Depends(get_trade_service) 
):
    try:
        result = service.get_order_list(segment,page,page_size)
        clean_result = sanitize_for_json(result)

        return{
            "status": "success",
            "order_list": clean_result
        }
    
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))   
    
@router.get("/order_detail")
def get_order_detail(
    groww_order_id:str=Query(..., example="GMK39038RDT490CCVRO"),
    segment:str=Query(..., example="CASH"),
    service: TradeService = Depends(get_trade_service) 
):
    try:
        result = service.get_order_detail(groww_order_id,segment)
        clean_result = sanitize_for_json(result)

        return{
            "status": "success",
            "order_detail": clean_result
        }
    
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# trade_controller.py

@router.post("/smart-order/gtt")
def place_gtt(
    request: GTTOrderRequestDTO,
    service: TradeService = Depends(get_trade_service)
):
    try:
        result = service.place_gtt_order(request)

        smart_order_id = (
            result.get("smart_order_id")
            or result.get("data", {}).get("smart_order_id")
        )

        if not smart_order_id:
            raise Exception(f"Invalid Groww response: {result}")

        return {
            "status": "success",
            "smart_order_id": smart_order_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    

@router.post("/smart-order/oco")
def place_oco(
    request: OCORequestDTO,
    service: TradeService = Depends(get_trade_service)
):
    try:
        if request.segment not in ["CASH", "FNO"]:
            raise HTTPException(
                status_code=400,
                detail="OCO smart order supported only for CASH and FNO"
            )

        result = service.place_oco_order(request)

        smart_order_id = (
            result.get("smart_order_id")
            or result.get("data", {}).get("smart_order_id")
        )

        if not smart_order_id:
            raise Exception(f"Invalid Groww response: {result}")

        return {
            "status": "success",
            "segment": request.segment,
            "smart_order_id": smart_order_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.put("/smart-order/gtt/modify")
def modify_gtt(
    request: ModifyGTTRequestDTO,
    service: TradeService = Depends(get_trade_service)
):
    
    print(request)

    try:
        result = service.modify_gtt_order(
            smart_order_id=request.smart_order_id,
            quantity=request.quantity,
            trigger_price=request.trigger_price,
            limit_price=request.limit_price,
            transaction_type=request.transaction_type
        )

        smart_order_id = (
            result.get("smart_order_id")
            or result.get("data", {}).get("smart_order_id")
        )

        if not smart_order_id:
            raise Exception(f"Invalid Groww response: {result}")

        return {
            "status": "success",
            "smart_order_id": smart_order_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

###
@router.put("/smart-order/gtt/modify-action")
def modify_gtt_action(
    request: ModifyGTTActionDTO,
    service: TradeService = Depends(get_trade_service)
):
    try:
        result = service.modify_gtt_with_action(request)

        smart_order_id = (
            result.get("smart_order_id")
            or result.get("data", {}).get("smart_order_id")
        )

        if not smart_order_id:
            raise Exception(f"Invalid Groww response: {result}")

        return {
            "status": "success",
            "smart_order_id": smart_order_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

###
    

@router.put("/smart-order/oco/modify")
def modify_oco(
    request: ModifyOCORequestDTO,
    service: TradeService = Depends(get_trade_service)
):
    try:
        result = service.modify_oco_order(request)

        smart_order_id = (
            result.get("smart_order_id")
            or result.get("data", {}).get("smart_order_id")
        )

        if not smart_order_id:
            raise Exception(f"Invalid Groww response: {result}")

        return {
            "status": "success",
            "smart_order_id": smart_order_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.put("/smart-order/oco/modify-action")
def modify_oco_action(
    request: ModifyOCOActionDTO,
    service: TradeService = Depends(get_trade_service)
):
    try:
        result = service.modify_oco_with_action(request)

        smart_order_id = (
            result.get("smart_order_id")
            or result.get("data", {}).get("smart_order_id")
        )

        if not smart_order_id:
            raise Exception(f"Invalid Groww response: {result}")

        return {
            "status": "success",
            "smart_order_id": smart_order_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

    
@router.put("/smart-order/cancel")
def cancel_smart_order(
    request: CancelSmartOrderRequestDTO,
    service: TradeService = Depends(get_trade_service)
):
    try:
        result = service.cancel_smart_order(request)

        smart_order_id = (
            result.get("smart_order_id")
            or result.get("data", {}).get("smart_order_id")
        )

        if not smart_order_id:
            raise Exception(f"Invalid Groww response: {result}")

        return {
            "status": "success,order cancel",
            "smart_order_id": smart_order_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/smart_order_detail")
def get_smart_order_details(
    segment:str=Query(..., example="CASH"),
    smart_order_type:str=Query(..., example="GTT"),
    smart_order_id:str=Query(..., example="GTT2601121322082FXEZLCMDS7W"),
    service: TradeService = Depends(get_trade_service) 
):
    try:
        result = service.get_smart_order_details(segment,smart_order_type,smart_order_id)
        clean_result = sanitize_for_json(result)

        return{
            "status": "success",
            "order_detail": clean_result
        }
    
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/smart_order_list")
def get_smart_order_list(
    segment:str=Query(..., example="CASH"),
    smart_order_type:str=Query(..., example="GTT"),
    status:str=Query(..., example="COMPLETED"),
    page:int=Query(..., example="0"),
    page_size:int=Query(..., example="10"),
    start_date_time:str=Query(..., example="2026-01-12T00:00:00"),
    end_date_time:str=Query(..., example="2026-01-12T23:59:59"),
    service: TradeService = Depends(get_trade_service) 
):
    try:
        result = service.get_smart_order_list(segment,smart_order_type,status,page,page_size,start_date_time,end_date_time)
        clean_result = sanitize_for_json(result)

        return{
            "status": "success",
            "order_list": clean_result
        }
    
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))



