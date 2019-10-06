from enum import Enum
from typing import List

from .rwmodel import RWModel


class Action(str, Enum):
    创建 = "创建"
    修改 = "修改"
    删除 = "删除"
    查看 = "查看"
    停用 = "停用"
    启用 = "启用"
    所有 = "*"


class ObjectAction(RWModel):
    url_prefix: str
    name: str
    actions: List[Action]


################################################
# 对象及其可能的操作
# 注意操作遵循一个原则，即如果没有标注他人的操作则表示是操作自己的对象，只有明确标注了他人字样的操作才是操作他人的对象的操作，如修改他人。
################################################
账户 = ObjectAction(url_prefix="/account", name="账户", actions=["创建", "修改", "查看", "删除", "停用", "启用"])
