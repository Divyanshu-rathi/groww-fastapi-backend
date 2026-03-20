from app.client.grow_client import GrowwClient
from app.utils.exceptions import TradeException
from app.service.user_service import UserService
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.models.instrument import Instrument
from app.models.user import User
import asyncio
from app.models.groww_session import GrowwSession
from app.service.base_groww_service import BaseGrowwService
from app.utils.price_helpers import calculate_price_with_action
from app.utils.order_helpers import filter_orders_by_symbol
from app.service.instrument_service import InstrumentService

class TradeService(BaseGrowwService):

    def __init__(self, user, ws_manager=None):
        super().__init__(user)
        self.ws_manager = ws_manager
        self.instrument_service = InstrumentService(user)


    def buy(
        self,
        symbol: str,
        quantity: int,
        segment: str = "CASH",
        product: str = None,
        order_type: str = "MARKET",
        price: float = None,
        trigger_price: float = None,
        validity: str = "DAY",
        exchange: str = "NSE",
        order_reference_id: str = None    
    ):
        try:
            response = self.groww_client.place_order_buy(
                symbol=symbol,
                quantity=quantity,
                segment=segment,
                product=product,
                order_type=order_type,
                price=price,
                trigger_price=trigger_price,
                validity=validity,
                exchange=exchange,
                order_reference_id=order_reference_id       
            )

            print("GROWW RESPONSE:", response)

            order_id = response.get("groww_order_id") or response.get("data", {}).get("groww_order_id")
            status = response.get("order_status") or response.get("status")
            remark = response.get("remark")

            success_status = ["new", "open", "complete", "success", "ok", "acked"]

            if status and str(status).lower() not in success_status:
                return {
                    "success": False,
                    "order_id": order_id,
                    "reason": remark
                }

            return {
                "success": True,
                "order_id": order_id,
                "status": status
            }

        
        except Exception as e:
            return {"success": False, "reason": str(e)}
        

    def place_limit_buy_from_ui(self, ui_request):
        try:
            if ui_request.transactionType.upper() != "BUY":
                return {"success": False, "reason": "Only BUY supported"}
            
            if ui_request.orderType.upper() != "LIMIT":
                return {"success": False, "reason": "Only LIMIT order supported"}
            
            if not ui_request.price or ui_request.price <= 0:
                return {"success": False, "reason": "Price required for LIMIT order"}
            
            instrument = self.instrument_service.get_instrument_by_exchange_and_trading_symbol(
                exchange=ui_request.exchange,
                trading_symbol=ui_request.tradingsymbol
            )

            if not instrument:
                return {"success": False, "reason": "Instrument not found"}
            
            if isinstance(instrument, dict):
                segment = instrument.get("segment")
            else:
                segment = instrument.segment

            if not segment:
                return {"success": False, "reason": "Segment not found"}


            product = ui_request.product or ("CNC" if segment == "CASH" else "MIS")

            response = self.groww_client.place_order_buy(
                symbol=ui_request.tradingsymbol,
                quantity=ui_request.quantity,
                segment=segment,
                product=product,
                order_type="LIMIT",
                price=ui_request.price,
                exchange=ui_request.exchange,
                validity=ui_request.validity or "DAY",
            )

            print("GROWW RAW RESPONSE:", response)

            order_id = (
                response.get("groww_order_id") or
                response.get("data", {}).get("groww_order_id")
            )

            status = response.get("order_status") or response.get("status")
            remark = response.get("remark")

            if not order_id:
                return {"success": False, "reason": f"Invalid Groww response: {response}"}
            
            ui_response = {
                "exchange_order_id": order_id,
                "status": status or "OPEN",
                "order_id": order_id,
                "tradingsymbol": ui_request.tradingsymbol,
                "price": str(ui_request.price),
                "quantity": str(ui_request.quantity),
                "transaction_type": "BUY",
                "product": product,
                "exchange": ui_request.exchange,
                "status_message": remark
            }

            return {"success": True, "data": ui_response}
        
        except Exception as e:
            return {"success": False, "reason": str(e)}
        


    def sell(
        self,
        symbol: str,
        quantity: int,
        segment: str = "CASH",
        product: str = None,
        order_type: str = "MARKET",
        price: float = None,
        trigger_price: float = None,
        validity: str = "DAY",
        exchange: str = "NSE",
        order_reference_id: str = None       
    ):
        try:
            response = self.groww_client.place_order_sell(
                symbol=symbol,
                quantity=quantity,
                segment=segment,
                product=product,
                order_type=order_type,
                price=price,
                trigger_price=trigger_price,
                validity=validity,
                exchange=exchange,
                order_reference_id=order_reference_id
            )

            order_id = response.get("groww_order_id") or response.get("data", {}).get("groww_order_id")
            status = response.get("order_status") or response.get("status")

            if not order_id:
                return {"success": False, "reason": f"Invalid Groww response: {response}"}
            
            return {
                "success": True,
                "order_id": order_id,
                "status": status or "success"
            }
        
        except Exception as e:
            return {"success": False, "reason": str(e)}



    def cancel(self, order_id: str, segment: str):
        try:
            return self.groww_client.cancel_order(order_id, segment)
        except Exception as e:
            raise TradeException(str(e))
        

    def bulk_cancel_by_symbol(self, request):
        try:
            segment_map = {
                "CASH": self.groww_client.client.SEGMENT_CASH,
                "FNO": self.groww_client.client.SEGMENT_FNO
            }

            segment_const = segment_map.get((request.segment or "").upper())

            if not segment_const:
                raise TradeException("Invalid segment")
            
            orders_resp = self.get_order_list(
                segment=request.segment,
                page=request.page,
                page_size=request.page_size
            )

            print("ORDERS RESPONSE:", orders_resp)

            order_list = orders_resp.get("data",{}).get("orders") or orders_resp.get("order_list") or []

            print("ORDER LIST:", order_list)

            if not isinstance(order_list, list):
                raise TradeException(f"Invalid Groww response for order list: {orders_resp}")
            
            same_symbol_orders = filter_orders_by_symbol(order_list, request.symbol)
            if not same_symbol_orders:
                return {
                    "status": "success",
                    "symbol": request.symbol,
                    "segment": request.segment,
                    "message": "No matching orders found",
                    "results": []
                }
            
            results = []
            for o in same_symbol_orders:
                order_id = o.get("groww_order_id")
                status = (o.get("order_status") or o.get("status") or "").upper()

                print("CHECKING ORDER:", order_id, status)

                if status not in ["OPEN", "NEW" , "ACKED","APPROVED", "PENDING", "TRIGGER_PENDING"]:
                    continue

                if not order_id:
                    results.append({"order_id": None, "status": "failed", "reason": "Missing groww_order_id"})
                    continue

                try:
                    self.cancel(order_id, request.segment)
                    results.append({"order_id": order_id, "status": "cancelled"})
                except Exception as e:
                    results.append({"order_id": order_id, "status": "failed", "reason": str(e)})

            return {
                "status": "success",
                "symbol": request.symbol,
                "segment": request.segment,
                "results": results
            }
            
        except Exception as e:
            raise TradeException(str(e))
        

    def bulk_modify_with_action_by_symbol(self, request):
        try:
            orders_resp = self.get_order_list(
                segment=request.segment,
                page=request.page,
                page_size=request.page_size
            )

            order_list = orders_resp.get("data") or orders_resp.get("order_list") or []
            if not isinstance(order_list, list):
                raise TradeException(f"Invalid Groww response for order list: {orders_resp}")
            
            same_symbol_orders = filter_orders_by_symbol(order_list, request.symbol)
            if not same_symbol_orders:
                return {
                    "status": "success",
                    "symbol": request.symbol,
                    "segment": request.segment,
                    "message": "No matching orders found",
                    "results": []
                }
            
            results = []
            for o in same_symbol_orders:
                order_id = o.get("groww_order_id")
                status = (o.get("order_status") or o.get("status") or "").upper()
                order_type = (o.get("order_type") or "").upper()
                quantity = o.get("quantity")

                if request.only_order_type and order_type != request.only_order_type:
                    continue

                if status not in ["NEW", "OPEN", "ACKED","APPROVED", "PENDING", "TRIGGER_PENDING"]:
                    continue

                if not order_id or not quantity:
                    results.append({
                        "order_id": order_id,
                        "status": "failed",
                        "reason": "Missing groww_order_id or quantity"
                    })
                    continue

                try:
                    if order_type == "LIMIT":
                        if request.price_field != "PRICE":
                            results.append({
                                "order_id": order_id,
                                "status": "skipped",
                                "reason": "LIMIT supports PRICE modification only"
                            })
                            continue

                        current_price = o.get("price")
                        new_price = calculate_price_with_action(current_price, request.action, request.step)

                        self.modify(
                            order_id=order_id,
                            quantity=quantity,
                            segment=request.segment,
                            order_type="LIMIT",
                            price=new_price,
                            trigger_price=None
                        )

                        results.append({
                            "order_id": order_id,
                            "status": "modified",
                            "updated": {"price": new_price}
                        })

                    elif order_type == "STOP_LOSS":
                        current_price = o.get("price")
                        current_trigger = o.get("trigger_price")

                        price = current_price
                        trigger = current_trigger

                        if request.price_field == "PRICE":
                            price = calculate_price_with_action(current_price, request.action, request.step)
                        elif request.price_field == "TRIGGER":
                            trigger = calculate_price_with_action(current_trigger, request.action, request.step)
                        else:
                            raise TradeException("Invalid price_field")
                        
                        self.modify(
                            order_id=order_id,
                            quantity=quantity,
                            segment=request.segment,
                            order_type="STOP_LOSS",
                            price=price,
                            trigger_price=trigger
                        )

                        results.append({
                            "order_id": order_id,
                            "status": "modified",
                            "updated": {"price": price, "trigger_price": trigger}
                        })


                    elif order_type == "STOP_LOSS_MARKET":
                        if request.price_field != "TRIGGER":
                            results.append({
                                "order_id": order_id,
                                "status": "skipped",
                                "reason": "STOP_LOSS_MARKET supports TRIGGER modification only"
                            })
                            continue

                        current_trigger = o.get("trigger_price")
                        new_trigger = calculate_price_with_action(current_trigger, request.action, request.step)

                        self.modify(
                            order_id=order_id,
                            quantity=quantity,
                            segment=request.segment,
                            order_type="STOP_LOSS_MARKET",
                            price=None,
                            trigger_price=new_trigger
                        )

                        results.append({
                            "order_id": order_id,
                            "status": "modified",
                            "updated": {"trigger_price": new_trigger}
                        })

                    else:
                        results.append({
                            "order_id": order_id,
                            "status": "skipped",
                            "reason": f"Unsupported order_type for modify: {order_type}"
                        })

                except Exception as e:
                    results.append({
                        "order_id": order_id,
                        "status": "failed",
                        "reason": str(e)
                    })

            return {
                "status": "success",
                "symbol": request.symbol,
                "segment": request.segment,
                "results": results
            }
        
        except Exception as e:
            raise TradeException(str(e))



   
    def modify(
        self,
        order_id: str,
        quantity: int,
        segment: str,
        order_type: str,
        price: float = None,
        trigger_price: float = None
    ):
        try:
            return self.groww_client.modify_order(
                groww_order_id=order_id,
                quantity=quantity,
                segment=segment,
                order_type=order_type,
                price=price,
                trigger_price=trigger_price
            )
        except Exception as e:
            raise TradeException(str(e))


    def bulk_modify_by_symbol(self, request):
        try:
            orders_resp = self.get_order_list(
                segment="CASH",
                page=request.page,
                page_size=request.page_size
            )

            orders_resp_fno = self.get_order_list(
                segment="FNO",
                page=request.page,
                page_size=request.page_size
            )

            order_list = (
                (orders_resp.get("order_list") or []) +
                (orders_resp_fno.get("order_list") or [])
            )

            print("ORDER LIST:", order_list)

            if not isinstance(order_list, list):
                raise TradeException(f"Invalid Groww response for order list")

            

            same_symbol_orders = filter_orders_by_symbol(order_list, request.symbol)

            if not same_symbol_orders:
                return {
                    "status": "success",
                    "symbol": request.symbol,
                    "segment": request.segment,
                    "message": "No matching orders found",
                    "results": []
                }
            
            results = []

            for o in same_symbol_orders:

                order_id = o.get("groww_order_id")

                status = (o.get("order_status") or o.get("status") or "").upper()
                order_type = (o.get("order_type") or "").upper()
                quantity = o.get("quantity")

                if request.order_type and order_type != request.order_type.upper():
                    continue

                if status not in ["NEW", "OPEN", "ACKED", "APPROVED", "PENDING", "TRIGGER_PENDING"]:
                    continue

                if not order_id or not quantity:
                    results.append({
                        "order_id": order_id,
                        "status": "failed",
                        "reason": "Missing groww_order_id or quantity"
                    })
                    continue

                try:
                    if order_type == "LIMIT":

                        if request.price is None:
                            results.append({
                                "order_id": order_id,
                                "status": "skipped",
                                "reason": "LIMIT modify requires price"
                            })
                            continue

                        self.modify(
                            order_id=order_id,
                            quantity=quantity,
                            segment=request.segment,
                            order_type="LIMIT",
                            price=request.price,
                            trigger_price=None
                        )

                        results.append({
                            "order_id": order_id,
                            "status": "modified",
                            "updated": {"price": request.price}
                        })

                    elif order_type == "STOP_LOSS":

                        if request.price is None or request.trigger_price is None:
                            results.append({
                                "order_id": order_id,
                                "status": "skipped",
                                "reason": "STOP_LOSS modify requires price & trigger_price"
                            })
                            continue

                        self.modify(
                            order_id=order_id,
                            quantity=quantity,
                            segment=o.get("segment") or request.segment,
                            order_type="STOP_LOSS",
                            price=request.price,
                            trigger_price=request.trigger_price
                        )

                        results.append({
                            "order_id": order_id,
                            "status": "modified",
                            "updated": {
                                "price": request.price,
                                "trigger_price": request.trigger_price
                            }
                        })

                    elif order_type == "STOP_LOSS_MARKET":

                        if request.trigger_price is None:
                            results.append({
                                "order_id": order_id,
                                "status": "skipped",
                                "reason": "STOP_LOSS_MARKET modify requires trigger_price"
                            })
                            continue

                        self.modify(
                            order_id=order_id,
                            quantity=quantity,
                            segment=request.segment,
                            order_type="STOP_LOSS_MARKET",
                            price=None,
                            trigger_price=request.trigger_price
                        )

                        results.append({
                            "order_id": order_id,
                            "status": "modified",
                            "updated": {"trigger_price": request.trigger_price}
                        })

                    else:
                        results.append({
                            "order_id": order_id,
                            "status": "skipped",
                            "reason": f"Unsupported order_type: {order_type}"
                        })
                        

                except Exception as e:

                    results.append({
                        "order_id": order_id,
                        "status": "failed",
                        "reason": str(e)
                    })

            return {
                "status": "success",
                "symbol": request.symbol,
                "segment": request.segment,
                "results": results
            }
        
        except Exception as e:
            raise TradeException(str(e))


        

    def modify_with_action(self, request):
        price = request.current_price
        trigger_price = request.current_trigger_price

        if request.order_type == "LIMIT":
            if request.price_field != "PRICE":
                raise TradeException("LIMIT order supports PRICE modification only")
            if price is None:
                raise TradeException("current_price required")
            
            price = calculate_price_with_action(price, request.action)

        elif request.order_type == "STOP_LOSS":
            if request.price_field == "PRICE":
                if price is None:
                    raise TradeException("current_price required")
                price = calculate_price_with_action(price, request.action)

            elif request.price_field == "TRIGGER":
                if trigger_price is None:
                    raise TradeException("current_trigger_price required")
                trigger_price = calculate_price_with_action(trigger_price, request.action)

        elif request.order_type == "STOP_LOSS_MARKET":
            if request.price_field != "TRIGGER":
                raise TradeException("STOP_LOSS_MARKET supports TRIGGER modification only")
            if trigger_price is None:
                raise TradeException("current_trigger_price required")
            
            trigger_price = calculate_price_with_action(trigger_price, request.action)

        else:
            raise TradeException("Invalid order_type")
        
        return self.modify(
            order_id=request.order_id,
            quantity=request.quantity,
            segment=request.segment,
            order_type=request.order_type,
            price=price,
            trigger_price=trigger_price
        )

      
        
    def get_tradelist_for_orders(self, groww_order_id:str,segment:str,page:int,page_size:int):
        try:
            return self.groww_client.get_tradelist_for_orders(groww_order_id,segment,page,page_size) 
        except Exception as e:
            raise TradeException(str(e))
        
    def get_order_status(self,groww_order_id:str,segment:str):
        try:
            return self.groww_client.get_order_status(groww_order_id,segment)
        except Exception as e:
            raise TradeException(str(e))
        
    def get_order_status_by_reference(self,order_reference_id:str,segment:str):
        try:
            return self.groww_client.get_order_status_by_reference(order_reference_id,segment)
        except Exception as e:
            raise TradeException(str(e))
        
    def get_order_list(self,segment:str,page:int,page_size:int):
        try:
            return self.groww_client.get_order_list(segment,page,page_size)
        except Exception as e:
            raise TradeException(str(e))
        
    def get_order_detail(self,groww_order_id:str,segment:str):
        try:
            return self.groww_client.get_order_detail(groww_order_id,segment)
        except Exception as e:
            raise TradeException(str(e))
        
    def place_gtt_order(self, request):
        try:
            return self.groww_client.place_gtt_order(
                symbol=request.symbol,
                quantity=request.quantity,
                trigger_price=request.trigger_price,
                limit_price=request.limit_price,
                transaction_type=request.transaction_type,
                trigger_direction=request.trigger_direction,
                reference_id=None,
                product_type=request.product_type
            )
        except Exception as e:
            raise TradeException(str(e))
        
    def place_oco_order(self,request):
        return self.groww_client.place_oco_order(
            symbol=request.symbol,
            quantity=request.quantity,
            segment=request.segment,
            product_type=request.product_type,
            target_trigger_price=request.target_trigger_price,
            target_price=request.target_price,
            stoploss_trigger_price=request.stoploss_trigger_price
        )
    
    def modify_gtt_order(
        self,
        smart_order_id: str,
        quantity: int,
        trigger_price: float,
        limit_price: float,
        transaction_type: str    
    ):
        try:
            return self.groww_client.modify_gtt_order(
                smart_order_id=smart_order_id,
                quantity=quantity,
                trigger_price=trigger_price,
                limit_price=limit_price,
                transaction_type=transaction_type
            )
        except Exception as e:
            raise TradeException(str(e))

    ###
    def modify_gtt_with_action(self, request):
        new_trigger_price = calculate_price_with_action(
            request.current_price,
            request.action
        )

        return self.modify_gtt_order(
            smart_order_id=request.smart_order_id,
            quantity=request.quantity,
            trigger_price=new_trigger_price,
            limit_price=request.limit_price,
            transaction_type=request.transaction_type
        ) 
        
    ###
        
    def modify_oco_order(self, request):
        try:
            return self.groww_client.modify_oco_order(
                smart_order_id=request.smart_order_id,
                quantity=request.quantity,
                target_trigger_price=request.target_trigger_price,
                target_price=request.target_price,
                stoploss_trigger_price=request.stoploss_trigger_price
            )
        except Exception as e:
            raise TradeException(str(e))
        

    def modify_oco_with_action(self, request):

        if request.price_type == "TARGET":
            new_target_trigger = calculate_price_with_action(
                request.current_target_trigger_price,
                request.action
            )

            new_stoploss_trigger = request.current_stoploss_trigger_price

        elif request.price_type == "STOPLOSS":
            new_stoploss_trigger = calculate_price_with_action(
                request.current_stoploss_trigger_price,
                request.action
            )
            new_target_trigger = request.current_target_trigger_price

        else:
            raise TradeException("Invalid price_type")
        
        return self.modify_oco_order(
            smart_order_id=request.smart_order_id,
            quantity=request.quantity,
            target_trigger_price=new_target_trigger,
            target_price=request.target_price,
            stoploss_trigger_price=new_stoploss_trigger
        )
    
        
    def cancel_smart_order(self, request):
        try:
            return self.groww_client.cancel_smart_order(
                smart_order_id=request.smart_order_id
            )
        except Exception as e:
            raise TradeException(str(e))
        
    def get_smart_order_details(self,segment:str,smart_order_type:str,smart_order_id:str):
        try:
            return self.groww_client.get_smart_order_details(segment,smart_order_type,smart_order_id)
        except Exception as e:
            raise TradeException(str(e))
        
    def get_smart_order_list(self,segment:str,smart_order_type:str,status:str,page:int,page_size:int,start_date_time:str,end_date_time:str):
        try:
            return self.groww_client.get_smart_order_list(segment,smart_order_type,status,page,page_size,start_date_time,end_date_time)
        except Exception as e:
            raise TradeException(str(e))




        
    
        
   
        


