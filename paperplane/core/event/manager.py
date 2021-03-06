import logging
from abc import ABC
from threading import Thread
import asyncio

from paperplane.core.event import EventEngine
from paperplane.core.trade.account import on_order_deal, on_order_cancel
from paperplane.core.trade.market import Exchange, ChinaAMarket
from paperplane.db.client.mongodb import get_client, get_database
from paperplane.models.event import EVENT_ERROR, EVENT_MARKET_CLOSE, EVENT_ORDER_DEAL, EVENT_ORDER_REJECTED


class EventManager:
    """模拟交易主引擎"""

    def __init__(self, event_engine: EventEngine = None, market: Exchange = None):
        # 绑定事件引擎
        if not event_engine:
            self.event_engine = EventEngine()
        else:
            self.event_engine = event_engine
        self.event_engine.start()

        self._db = None  # 数据库实例
        self._market = market  # 市场实例

        # 开启邮件引擎
        # TODO

        # 市场交易线程
        self._event_loop = asyncio.get_event_loop()
        self._thread = Thread(target=self._run)

        # 注册事件监听
        self.event_register()

        logging.info("模拟交易主引擎：初始化完毕")

    def event_register(self):
        """注册事件监听"""
        self.event_engine.register(EVENT_ERROR, self.process_error_event)
        self.event_engine.register(EVENT_MARKET_CLOSE, self.process_market_close)
        self.event_engine.register(EVENT_ORDER_DEAL, self.process_order_deal)
        self.event_engine.register(EVENT_ORDER_REJECTED, self.process_order_rejected)

    def start(self):
        """引擎初始化"""
        logging.info("模拟交易主引擎：启动")

        # 默认使用ChinaAMarket
        if not self._market:
            self._market = ChinaAMarket(self.event_engine)

        # 获取数据库连接
        self._dbclient = get_client()

        # 连接数据库
        self._db = get_database()

        # 启动订单薄撮合程序
        self._thread.start()

        return True

    def _run(self):
        """订单薄撮合程序启动"""
        asyncio.run_coroutine_threadsafe(self._market.on_match(self._db), self._event_loop)

    def _close(self):
        """模拟交易引擎关闭"""
        # 关闭市场
        self._thread.join(3)

        # 关闭数据库
        self._dbclient.close()

        # 关闭事件引擎
        self.event_engine.stop()

        logging.info("模拟交易主引擎：关闭")

    def process_order_deal(self, event):
        """订单成交处理"""
        order = event.data
        asyncio.run_coroutine_threadsafe(on_order_deal(order, self._db), self._event_loop)

    def process_order_rejected(self, event):
        """订单拒单处理"""
        order = event.data
        asyncio.run_coroutine_threadsafe(on_order_cancel(order, self._db), self._event_loop)

    def process_market_close(self, event):
        """市场关闭处理"""
        market_name = event.data
        logging.info(f"{market_name}: 交易市场已经关闭")

    def process_error_event(self, event):
        """系统错误处理"""
        msg = event.data
        logging.critical(msg)
        self._close()


class BaseEngine(ABC):
    """
    Abstract class for implementing an function engine.
    """

    def __init__(self, event_engine: EventEngine, engine_name: str):
        """"""
        self.event_engine = event_engine
        self.engine_name = engine_name

    def close(self):
        """"""
        pass


me = None


async def start_engine():
    global me
    # 初始化撮合引擎
    me = EventManager()
    # 开启模拟交易引擎
    if me.start():
        logging.info("撮合引擎启动成功！")
    else:
        logging.critical("撮合引擎启动失败！")


async def stop_engine():
    global me
    me._close()
