from growwapi import GrowwAPI
from growwapi.groww.exceptions import GrowwAPIException
from app.utils.exceptions import TradeException
import time
import random
import string
from typing import Optional,Any, Dict

class GrowwClient:
    def __init__(self, access_token: str):
        try:
            self.client = GrowwAPI(access_token)

        except Exception as e:
            raise TradeException(f"Groww client init failed: {str(e)}")
        

    def place_order_buy(
            self,
            symbol: str,
            quantity: int,
            segment: str,
            product: Optional[str] = None,
            order_type: str = "MARKET",
            price: Optional[float] = None,
            trigger_price: Optional[float] = None,
            validity: str = "DAY",
            exchange: str = "NSE",
            order_reference_id: Optional[str] = None
    ):
        
        try:
            segment_map = {
                "CASH": self.client.SEGMENT_CASH,
                "FNO": self.client.SEGMENT_FNO
            }

            product_map ={
                "CNC": self.client.PRODUCT_CNC,
                "MIS": self.client.PRODUCT_MIS,
                "NRML": self.client.PRODUCT_NRML
            }

            order_type_map = {
                "MARKET": self.client.ORDER_TYPE_MARKET,
                "LIMIT": self.client.ORDER_TYPE_LIMIT,
                "STOP_LOSS": self.client.ORDER_TYPE_STOP_LOSS,
                "STOP_LOSS_MARKET": self.client.ORDER_TYPE_STOP_LOSS_MARKET
            }

            validity_map = {
                "DAY": self.client.VALIDITY_DAY,
            }

            exchange_map = {
                "NSE": self.client.EXCHANGE_NSE,
                "BSE": self.client.EXCHANGE_BSE,
                "MCX": self.client.EXCHANGE_MCX,
            }

            segment_key = (segment or "").upper()
            segment_const = segment_map.get(segment_key)
            if not segment_const:
                raise TradeException("Invalid segment. Allowed: CASH, FNO")
            
            if not product:
                product = "CNC" if segment_key == "CASH" else "MIS"

            product_key = product.upper()
            product_const = product_map.get(product_key)
            if not product_const:
                raise TradeException("Invalid product type. Allowed: CNC, MIS, NRML")
            
            order_type_key = (order_type or "MARKET").upper()
            order_type_const = order_type_map.get(order_type_key)
            if not order_type_const:
                raise TradeException(
                    "Invalid order_type. Allowed: MARKET, LIMIT, STOP_LOSS, STOP_LOSS_MARKET"
                )


            validity_key = (validity or "DAY").upper()
            validity_const = validity_map.get(validity_key)
            if not validity_const:
                raise TradeException("Invalid validity. Allowed: DAY")
            
            exchange_key = (exchange or "NSE").upper()
            exchange_const = exchange_map.get(exchange_key)
            if not exchange_const:
                raise TradeException("Invalid exchange. Allowed: NSE, BSE, MCX")
            
            final_price: float = 0.0
            final_trigger: Optional[float] = None

            if order_type_key == "MARKET":
                final_price = 0.0
                final_trigger = None

            elif order_type_key == "LIMIT":
                if price is None or price <= 0:
                    raise TradeException("For LIMIT order, 'price' is required and must be > 0")
                final_price = float(price)
                final_trigger = None

            elif order_type_key == "STOP_LOSS":
                if trigger_price is None or trigger_price <= 0:
                    raise TradeException("For STOP_LOSS order, 'trigger_price' is required and must be > 0")
                if price is None or price <= 0:
                    raise TradeException("For STOP_LOSS order, 'price' is required (limit price) and must be > 0")
                final_price = float(price)
                final_trigger = float(trigger_price)

            elif order_type_key == "STOP_LOSS_MARKET":
                if trigger_price is None or trigger_price <= 0:
                    raise TradeException(
                        "For STOP_LOSS_MARKET order, 'trigger_price' is required and must be > 0"
                    )
                final_price = 0.0
                final_trigger = float(trigger_price)

            payload = {
                "trading_symbol": symbol,
                "quantity": quantity,
                "validity": validity_const,
                "exchange": exchange_const,
                "segment": segment_const,
                "product": product_const,
                "order_type": order_type_const,
                "transaction_type": self.client.TRANSACTION_TYPE_BUY,
                "price": final_price,
            }

            if final_trigger is not None:
                payload["trigger_price"] = final_trigger

            if order_reference_id:
                payload["order_reference_id"] = order_reference_id

            return self.client.place_order(**payload)
        
        except GrowwAPIException as e:
            raise TradeException(f"Groww rejected order [{e.code}]: {e.msg}")
        

    def place_order_sell(
        self,
        symbol: str,
        quantity: int,
        segment: str,
        product: Optional[str] = None,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        validity: str = "DAY",
        exchange: str = "NSE",
        order_reference_id: Optional[str] = None    
    ):
        try:

            segment_map = {
                "CASH": self.client.SEGMENT_CASH,
                "FNO": self.client.SEGMENT_FNO
            }

            product_map = {
                "CNC": self.client.PRODUCT_CNC,
                "MIS": self.client.PRODUCT_MIS,
                "NRML": self.client.PRODUCT_NRML 
            }

            order_type_map = {
                "MARKET": self.client.ORDER_TYPE_MARKET,
                "LIMIT": self.client.ORDER_TYPE_LIMIT,
                "STOP_LOSS": self.client.ORDER_TYPE_STOP_LOSS,
                "STOP_LOSS_MARKET": self.client.ORDER_TYPE_STOP_LOSS_MARKET
            }

            validity_map = {
                "DAY": self.client.VALIDITY_DAY
            }

            exchange_map = {
                 "NSE": self.client.EXCHANGE_NSE,
                 "BSE": self.client.EXCHANGE_BSE,
                 "MCX": self.client.EXCHANGE_MCX
            }

            segment_key = segment.upper()
            segment_const = segment_map.get(segment_key)
            if not segment_const:
                raise TradeException("Invalid segment")
            
            if not product:
                product = "CNC" if segment_key == "CASH" else "MIS"

            product_const = product_map.get(product.upper())
            if not product_const:
                raise TradeException("Invalid product")
            
            order_type_key = order_type.upper()
            order_type_const = order_type_map.get(order_type_key)
            if not order_type_const:
                raise TradeException("Invalid order_type")
            
            validity_const = validity_map.get(validity.upper())
            exchange_const = exchange_map.get(exchange.upper())

            final_price = 0.0
            final_trigger = None

            if order_type_key == "MARKET":
                final_price = 0.0

            elif order_type_key == "LIMIT":
                if not price or price <= 0:
                    raise TradeException("LIMIT sell needs valid price")
                final_price = float(price)

            elif order_type_key == "STOP_LOSS":
                if not trigger_price or not price:
                    raise TradeException("STOP_LOSS sell needs price & trigger_price")
                final_price = float(price)
                final_trigger = float(trigger_price)

            elif order_type_key == "STOP_LOSS_MARKET":
                if not trigger_price:
                    raise TradeException("STOP_LOSS_MARKET sell needs trigger_price")
                final_price = 0.0
                final_trigger = float(trigger_price)

            payload = {
                "trading_symbol": symbol,
                "quantity": quantity,
                "validity": validity_const,
                "exchange": exchange_const,
                "segment": segment_const,
                "product": product_const,
                "order_type": order_type_const,
                "transaction_type": self.client.TRANSACTION_TYPE_SELL,
                "price": final_price
            }

            if final_trigger is not None:
                payload["trigger_price"] = final_trigger

            if order_reference_id:
                payload["order_reference_id"] = order_reference_id

            return self.client.place_order(**payload)
        

        except GrowwAPIException as e:
            raise TradeException(f"Groww rejected SELL order [{e.code}]: {e.msg}")
        

    
    def cancel_order(self, groww_order_id: str, segment:str):

        segment_map ={
            "CASH": self.client.SEGMENT_CASH,
            "FNO": self.client.SEGMENT_FNO,
        }

        segment_const = segment_map.get(segment.upper())

        if not segment_const:
            raise TradeException("Invalid segment")
        
        return self.client.cancel_order(
            segment= segment_const,
            groww_order_id=groww_order_id
        )

    def modify_order(
        self,
        groww_order_id: str,
        quantity: int,
        segment: str,
        order_type: str,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None
    ):
        
        segment_map ={
            "CASH": self.client.SEGMENT_CASH,
            "FNO": self.client.SEGMENT_FNO,
        }

        order_type_map = {
            "LIMIT": self.client.ORDER_TYPE_LIMIT,
            "STOP_LOSS": self.client.ORDER_TYPE_STOP_LOSS,
            "STOP_LOSS_MARKET": self.client.ORDER_TYPE_STOP_LOSS_MARKET,
        }

        segment_const = segment_map.get(segment.upper())
        if not segment_const:
            raise TradeException("Invalid segment")
        
        order_type_key = order_type.upper()
        order_type_const = order_type_map.get(order_type_key)
        if not order_type_const:
            raise TradeException("Invalid or non-modifiable order type")
        
        payload = {
            "groww_order_id": groww_order_id,
            "quantity": quantity,
            "segment": segment_const,
            "order_type": order_type_const
        }

        if order_type_key == "LIMIT":
            if price is None or price <= 0:
                raise TradeException("LIMIT modify requires valid price")
            payload["price"] = float(price)

        elif order_type_key == "STOP_LOSS":
            if price is None or trigger_price is None:
                raise TradeException("STOP_LOSS modify requires price & trigger_price")
            payload["price"] = float(price)
            payload["trigger_price"] = float(trigger_price)

        elif order_type_key == "STOP_LOSS_MARKET":
            if trigger_price is None:
                raise TradeException("STOP_LOSS_MARKET modify requires trigger_price")
            payload["trigger_price"] = float(trigger_price)


        
        return self.client.modify_order(**payload)


    def get_tradelist_for_orders(self, groww_order_id:str,segment:str,page:int,page_size:int):
        try:
            return self.client.get_trade_list_for_order(
                groww_order_id=groww_order_id,
                segment=segment,
                page=page,
                page_size=page_size
            )
        except Exception as e :
            raise TradeException(str(e))
        
    def get_order_status(self,groww_order_id:str,segment:str):
        try:
            return self.client.get_order_status(
                groww_order_id=groww_order_id,
                segment=segment
            )
        except Exception as e :
            raise TradeException(str(e))
        
    def get_order_status_by_reference(self,order_reference_id:str,segment:str):
        try:
            return self.client.get_order_status_by_reference(
                order_reference_id=order_reference_id,
                segment=segment
            )
        except Exception as e :
            raise TradeException(str(e))
        
    def get_order_list(self,segment:str,page:int,page_size:int):
        try:
            return self.client.get_order_list(
                segment=segment,
                page=page,
                page_size=page_size
            )
        except Exception as e :
            raise TradeException(str(e))
        
    def get_order_detail(self,groww_order_id:str,segment:str):
        try:
            return self.client.get_order_detail(
                groww_order_id=groww_order_id,
                segment=segment
            )
        except Exception as e :
            print("Groww API Error:", e) 
            raise TradeException(str(e))
        


    def _generate_reference_id(self) -> str:
        prefix = "GTT-C" 
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        ts = str(int(time.time()))[-6:]

        return f"{prefix}-{rand}{ts}"

        
    def place_gtt_order(
            self,
            symbol: str,
            quantity: int,
            trigger_price: float,
            limit_price: float,
            transaction_type: str, 
            trigger_direction: Optional[str] = None,
            reference_id: Optional[str]=None,
            product_type: Optional[str]=None
            
    ):
        try:
            segment = self.client.SEGMENT_CASH 

            product_map = {
                "CNC": self.client.PRODUCT_CNC,
                "MIS": self.client.PRODUCT_MIS,
                "NRML": self.client.PRODUCT_NRML
            }

            product_type = (product_type or "CNC").upper()
            product = product_map.get(product_type)
            if not product:
                raise TradeException("Invalid product_type. Allowed: CNC, MIS, NRML")
            
            txn_map = {
                "BUY": self.client.TRANSACTION_TYPE_BUY,
                "SELL": self.client.TRANSACTION_TYPE_SELL
            }
            txn_key = (transaction_type or "").upper()
            txn_const = txn_map.get(txn_key)
            if not txn_const:
                raise TradeException("Invalid transaction_type. Allowed: BUY, SELL")
            
            if not trigger_direction:
                trigger_direction = "DOWN" if txn_key == "BUY" else "UP"

            trig_dir_map ={
                "UP": self.client.TRIGGER_DIRECTION_UP,
                "DOWN": self.client.TRIGGER_DIRECTION_DOWN
            }

            trig_dir_const = trig_dir_map.get(trigger_direction.upper())
            if not trig_dir_const:
                raise TradeException("Invalid trigger_direction. Allowed: UP, DOWN")
            
            if quantity <= 0:
                raise TradeException("quantity must be > 0")
            
            if trigger_price <= 0:
                raise TradeException("trigger_price must be > 0")
            
            if limit_price <= 0:
                raise TradeException("limit_price must be > 0")

            reference_id = reference_id or self._generate_reference_id()

            return self.client.create_smart_order(
                smart_order_type=self.client.SMART_ORDER_TYPE_GTT,
                reference_id=reference_id,
                segment=segment,
                trading_symbol=symbol,
                quantity=quantity,
                product_type=product,
                exchange=self.client.EXCHANGE_NSE,
                duration=self.client.VALIDITY_DAY,

                trigger_price=str(trigger_price),
                trigger_direction=trig_dir_const,

                order={
                    "order_type": self.client.ORDER_TYPE_LIMIT,
                    "price": str(limit_price),
                    "transaction_type": txn_const
                }
            )
        
        except Exception as e:
            raise TradeException(str(e))
            
    def place_oco_order(
            self,
            symbol:str,
            quantity:int,
            segment:str,
            product_type:str,
            target_trigger_price:float,
            target_price:float,
            stoploss_trigger_price:float,
    ):
        try:

            segment_map = {
                "CASH": self.client.SEGMENT_CASH,
                "FNO": self.client.SEGMENT_FNO
            }

            if segment not in segment_map:
                raise ValueError("invalid segment. , allowed cash and fno")
            
            product_map = {
                "CNC": self.client.PRODUCT_CNC,
                "MIS": self.client.PRODUCT_MIS,
                "NRML": self.client.PRODUCT_NRML
            }

            if segment == "CASH":
                product_type = product_type or "CNC"
            else:
                product_type = product_type or "MIS"

            product = product_map[product_type]

            reference_id = self._generate_reference_id()

            return self.client.create_smart_order(
                smart_order_type=self.client.SMART_ORDER_TYPE_OCO,
                reference_id=reference_id,
                segment=segment_map[segment],
                trading_symbol=symbol,
                quantity=quantity,
                product_type=product,
                exchange=self.client.EXCHANGE_NSE,
                duration=self.client.VALIDITY_DAY,


                net_position_quantity=quantity,
                transaction_type=self.client.TRANSACTION_TYPE_SELL,

                target={
                    "trigger_price":str(target_trigger_price),
                    "order_type":self.client.ORDER_TYPE_LIMIT,
                    "price":str(target_price)
                },

                stop_loss={
                    "trigger_price":str(stoploss_trigger_price),
                    "order_type":self.client.ORDER_TYPE_STOP_LOSS_MARKET,
                }
            )
        
        except Exception as e:
            raise TradeException(str(e))

    def modify_gtt_order(
            self,
            smart_order_id: str,
            quantity: int,
            trigger_price: float, 
            limit_price: float,
            transaction_type: str  
    ):
        try:
            smart_order_id = smart_order_id.lower()

            txn_const = (
                self.client.TRANSACTION_TYPE_BUY
                if transaction_type.upper() == "BUY"
                else self.client.TRANSACTION_TYPE_SELL
            )

            
            trigger_direction = (
                self.client.TRIGGER_DIRECTION_DOWN
                if transaction_type.upper() == "BUY"
                else self.client.TRIGGER_DIRECTION_UP
            )


            return self.client.modify_smart_order(
                smart_order_id=smart_order_id,
                smart_order_type=self.client.SMART_ORDER_TYPE_GTT,
                segment = self.client.SEGMENT_CASH,
                quantity=quantity,
                trigger_price=str(trigger_price),
                trigger_direction=trigger_direction,
                order={
                    "order_type": self.client.ORDER_TYPE_LIMIT,
                    "price": str(limit_price),
                    "transaction_type": txn_const
                }
            ) 
        
        except Exception as e:
            raise TradeException(str(e))

  
    def _detect_smart_order_segment(self, smart_order_id, smart_order_type):
        for segment in [self.client.SEGMENT_CASH, self.client.SEGMENT_FNO]:
            try:
                order = self.client.get_smart_order(
                    smart_order_id=smart_order_id,
                    smart_order_type=smart_order_type,
                    segment=segment
                )
                return segment, order
            except Exception:
                continue

        raise TradeException("Smart order not found in CASH or FNO segment")

        
    def modify_oco_order(
        self,
        smart_order_id: str,
        quantity: int,
        target_trigger_price: float,
        target_price: float,
        stoploss_trigger_price: float
    ):
        try:
            segment, oco = self._detect_smart_order_segment(
                smart_order_id=smart_order_id,
                smart_order_type=self.client.SMART_ORDER_TYPE_OCO
            )


            status = oco.get("status")
            if status not in ["ACTIVE", "OPEN"]:
                raise TradeException(
                    f"OCO order not modifiable. Current status: {status}"
                )

            if segment.upper() == "CASH":
                segment_const = self.client.SEGMENT_CASH
            elif segment.upper() == "FNO":
                segment_const = self.client.SEGMENT_FNO
            else:
                raise TradeException("Invalid segment for OCO")
            
            return self.client.modify_smart_order(
                smart_order_id=smart_order_id,
                smart_order_type=self.client.SMART_ORDER_TYPE_OCO,
                segment=segment_const,
                quantity=quantity,

                target={
                    "trigger_price": str(target_trigger_price),
                    "order_type": self.client.ORDER_TYPE_LIMIT,
                    "price": str(target_price),
                },
                stop_loss={
                    "trigger_price": str(stoploss_trigger_price),
                    "order_type": self.client.ORDER_TYPE_STOP_LOSS_MARKET
                }          
            )
        
        except Exception as e:
            raise TradeException(str(e))
        
    def cancel_smart_order(self, smart_order_id: str):
        try:
            if smart_order_id.upper().startswith("GTT"):
                smart_order_type = self.client.SMART_ORDER_TYPE_GTT
            elif smart_order_id.upper().startswith("OCO"): 
                smart_order_type = self.client.SMART_ORDER_TYPE_OCO
            else:
                raise TradeException("Invalid smart order id")
              
            segment, smart_order = self._detect_smart_order_segment(
                smart_order_id=smart_order_id,
                smart_order_type=smart_order_type
            )

            status = smart_order.get("status")

            if status not in ["ACTIVE", "OPEN"]:
                raise TradeException(
                    f"Smart order not cancellable. Current status: {status}"
                )
            
            return self.client.cancel_smart_order(
                segment=segment,
                smart_order_type=smart_order_type,
                smart_order_id=smart_order_id
            )
        
        except Exception as e:
            raise TradeException(str(e))
        
    def get_smart_order_details(self,segment:str,smart_order_type:str,smart_order_id:str):
        try:
            return self.client.get_smart_order(
                segment=segment,
                smart_order_type=smart_order_type,
                smart_order_id=smart_order_id
            )
        except Exception as e:
            raise TradeException (str(e))
        
    def get_smart_order_list(self,segment:str,smart_order_type:str,status:str,page:int,page_size:int,start_date_time:str,end_date_time:str):
        try:
            return self.client.get_smart_order_list(
                segment=segment,
                smart_order_type=smart_order_type,
                status=status,
                page=page,
                page_size=page_size,
                start_date_time=start_date_time,
                end_date_time=end_date_time
            )
        except Exception as e:
            raise TradeException(str(e))

            


        
    














