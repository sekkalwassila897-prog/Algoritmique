from __future__ import annotations
from typing import List, Optional, Tuple
import bisect
import math

# ============================================
# ⚙️ تعريف العقدة (B* Node)
# ============================================
class BStarNode:
    def __init__(self, leaf: bool = True):
        self.leaf: bool = leaf
        self.keys: List[int] = []
        self.children: List[BStarNode] = []

    def is_full(self, m: int) -> bool:
        return len(self.keys) >= m

    def __repr__(self):
        return f"BStarNode(leaf={self.leaf}, keys={self.keys})"

# ============================================
# 🌳 تعريف شجرة B* (BStarTree)
# ============================================
class BStarTree:
    def __init__(self, order: int = 7):
        if order < 3:
            raise ValueError("Order must be >= 3")
        self.m = order
        self.kmin = round(2 * (self.m - 1) / 3)
        self.kmax = self.m - 1
        self.root = BStarNode(leaf=True)

    # --------------------------------------------
    # 🔍 البحث عن مفتاح
    # --------------------------------------------
    def search(self, key: int) -> Tuple[Optional[BStarNode], int]:
        node = self.root
        while node:
            i = bisect.bisect_left(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                return node, i
            if node.leaf:
                return None, -1
            node = node.children[i]
        return None, -1

    # --------------------------------------------
    # ➕ إدراج مفتاح جديد
    # --------------------------------------------
    def insert(self, key: int):
        print(f"\n=== INSERT {key} ===")
        root = self.root

        if not root.keys:
            bisect.insort(root.keys, key)
            return

        if root.is_full(self.m):
           if root.leaf:
              old_root = self.root
              new_root = BStarNode(leaf=False)
              new_root.children.append(old_root)
              self.root = new_root
              self._split_child(new_root, 0)
              return
           else :
               left = root.children[0]
               right = root.children[1] if len(root.children) > 1 else None
               if left and len(left.keys) < self.kmax:
                 self._redistribute(root, 0)
               elif right and len(right.keys) < self.kmax:
                 self._redistribute(root, 0)
               else:
                 self._three_way_split_strict(root, 0)

        self._insert_nonfull(self.root, key)

    # --------------------------------------------
    # 🌿 إدراج في عقدة غير ممتلئة
    # --------------------------------------------
    def _insert_nonfull(self, node: BStarNode, key: int, parent: Optional[BStarNode] = None, idx_in_parent: int = -1):
        if node.leaf:
            bisect.insort(node.keys, key)

            if len(node.keys) > self.kmax:

                if parent is None:
                    old_root = self.root
                    new_root = BStarNode(leaf=False)
                    new_root.children.append(old_root)
                    self.root = new_root
                    self._split_child(new_root, 0)
                else:
                    left_sib = parent.children[idx_in_parent - 1] if idx_in_parent - 1 >= 0 else None
                    right_sib = parent.children[idx_in_parent + 1] if idx_in_parent + 1 < len(parent.children) else None

                    if left_sib and len(left_sib.keys) < self.kmin:
                        self._redistribute(parent, idx_in_parent - 1)
                    elif right_sib and len(right_sib.keys) < self.kmin:
                        self._redistribute(parent, idx_in_parent)
                    elif left_sib and len(left_sib.keys) < self.kmax :
                        self._redistribute(parent, idx_in_parent - 1)
                    elif right_sib and len(right_sib.keys) < self.kmax:
                        self._redistribute(parent, idx_in_parent)
                    else:
                        if left_sib:
                            self._three_way_split_strict(parent, idx_in_parent - 1)
                        elif right_sib:
                            self._three_way_split_strict(parent, idx_in_parent)
            return

        i = bisect.bisect_left(node.keys, key)
        child = node.children[i]

        if not child.is_full(self.m):
            self._insert_nonfull(child, key, node, i)
        else:
            left_sib = node.children[i - 1] if i - 1 >= 0 else None
            right_sib = node.children[i + 1] if i + 1 < len(node.children) else None

            if left_sib and len(left_sib.keys) < self.kmax:
                self._redistribute(node, i - 1)
            elif right_sib and len(right_sib.keys) < self.kmax:
                self._redistribute(node, i)
            else:
                self._three_way_split_strict(node, i if right_sib else i - 1)

            self._insert_nonfull(node, key, parent, idx_in_parent)

    # --------------------------------------------
    # ✂️ تقسيم عادي لابن
    # --------------------------------------------
    def _split_child(self, parent: BStarNode, idx: int):
        full_child = parent.children[idx]
        mid = len(full_child.keys) // 2
        new_node = BStarNode(leaf=full_child.leaf)
        parent.keys.insert(idx, full_child.keys[mid])
        new_node.keys = full_child.keys[mid + 1:]
        full_child.keys = full_child.keys[:mid]

        if not full_child.leaf:
            new_node.children = full_child.children[mid + 1:]
            full_child.children = full_child.children[:mid + 1]

        parent.children.insert(idx + 1, new_node)

    # --------------------------------------------
    # 🔄 إعادة توزيع (Redistribution)
    # --------------------------------------------
    def _redistribute(self, parent: BStarNode, idx: int):
        L = parent.children[idx]
        R = parent.children[idx + 1]

        if len(L.keys) < self.kmin or len(L.keys) < len(R.keys):
            sep = parent.keys[idx]
            moved_up = R.keys.pop(0)
            L.keys.append(sep)
            parent.keys[idx] = moved_up
            if R.children:
                L.children.append(R.children.pop(0))
        else:
            sep = parent.keys[idx]
            moved_up = L.keys.pop()
            R.keys.insert(0, sep)
            parent.keys[idx] = moved_up
            if L.children:
                R.children.insert(0, L.children.pop())

    # --------------------------------------------
    # 💥 تقسيم صارم بثلاث عقد (3-way split)
    # --------------------------------------------
    def _three_way_split_strict(self, parent: BStarNode, idx_parent: int, new_key: Optional[int] = None):
        L = parent.children[idx_parent]
        R = parent.children[idx_parent + 1]
        sep = parent.keys[idx_parent]

        merged = L.keys + [sep] + R.keys
        if new_key is not None:
            merged.append(new_key)
        merged.sort()

        n = len(merged)
        if n < 3:
            return

        up1_idx = n // 3
        up2_idx = (2 * n) // 3
        up1 = merged[up1_idx]
        up2 = merged[up2_idx]

        P_keys = merged[:up1_idx]
        Q_keys = merged[up1_idx + 1: up2_idx]
        R_keys = merged[up2_idx + 1:]

        parent.keys[idx_parent:idx_parent+1] = [up1, up2]

        left_node = BStarNode(leaf=L.leaf)
        middle_node = BStarNode(leaf=L.leaf)
        right_node = BStarNode(leaf=R.leaf)

        left_node.keys = P_keys
        middle_node.keys = Q_keys
        right_node.keys = R_keys

        parent.children[idx_parent] = left_node
        parent.children[idx_parent + 1] = middle_node
        parent.children.insert(idx_parent + 2, right_node)

        if len(parent.keys) > self.kmax:
            if parent is self.root:
                old_root = self.root
                new_root = BStarNode(leaf=False)
                new_root.children.append(old_root)
                self.root = new_root
                self._split_child(new_root, 0)

    # --------------------------------------------
    # ❌ حذف مفتاح
    # --------------------------------------------
    def delete(self, key: int):
        print(f"\n=== DELETE {key} ===")
        if self.root is None or not self.root.keys:
            return
        self._delete_internal(self.root, key)

        if not self.root.keys and not self.root.leaf:
            self.root = self.root.children[0]

    # --------------------------------------------
    # 🧩 الحذف الداخلي
    # --------------------------------------------
    def _delete_internal(self, node: BStarNode, key: int, parent: Optional[BStarNode] = None, idx_in_parent: int = -1):
        i = bisect.bisect_left(node.keys, key)
        child = None

        if node.leaf:
            if i < len(node.keys) and node.keys[i] == key:
                node.keys.pop(i)
            else:
                return

        elif i < len(node.keys) and node.keys[i] == key:
            pred_node = node.children[i]
            while not pred_node.leaf:
                pred_node = pred_node.children[-1]
            predecessor = pred_node.keys[-1]
            node.keys[i] = predecessor
            child = node.children[i]
            self._delete_internal(child, predecessor, node, i)
        else:
            child = node.children[i]
            self._delete_internal(child, key, node, i)

        if len(node.keys) < self.kmin and parent is not None:
            self._fix_underflow(parent, idx_in_parent)

    # --------------------------------------------
    # 🔧 تصحيح بعد الحذف
    # --------------------------------------------
    def _fix_underflow(self, parent: BStarNode, idx: int):
        child = parent.children[idx]
        left_sib = parent.children[idx - 1] if idx - 1 >= 0 else None
        right_sib = parent.children[idx + 1] if idx + 1 < len(parent.children) else None

        if left_sib and len(left_sib.keys) > self.kmin:
            self._redistribute(parent, idx - 1)
        elif right_sib and len(right_sib.keys) > self.kmin:
            self._redistribute(parent, idx)
        else:
            if left_sib:
                self._merge_nodes(parent, idx - 1)
                merged_node = parent.children[idx - 1]
            elif right_sib:
                self._merge_nodes(parent, idx)
                merged_node = parent.children[idx]

            if len(merged_node.keys) > self.kmax:
                idx_parent = parent.children.index(merged_node)
                self._three_way_split_strict(parent, idx_parent)

    # --------------------------------------------
    # 🔗 دمج عقدتين
    # --------------------------------------------
    def _merge_nodes(self, parent: BStarNode, idx: int):
        left = parent.children[idx]
        right = parent.children[idx + 1]
        sep = parent.keys.pop(idx)

        left.keys.append(sep)
        left.keys.extend(right.keys)

        if not left.leaf:
            left.children.extend(right.children)

        parent.children.pop(idx + 1)

        if parent is self.root and not parent.keys:
            self.root = left
        elif parent is not self.root and len(parent.keys) < self.kmin:
            self._fix_underflow(parent, parent.children.index(left))
