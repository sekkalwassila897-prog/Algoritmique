from typing import List, Optional, Tuple
import uuid


class BTreeNode:
    def __init__(self, leaf: bool = True):
        self.leaf: bool = leaf
        self.keys: List[int] = []
        self.children: List['BTreeNode'] = []
        self.parent: Optional['BTreeNode'] = None  # nécessaire pour la montée
        self._id = str(uuid.uuid4())[:8]

    def __repr__(self):
        return f"Node(keys={self.keys}, leaf={self.leaf})"


class bTree:
    def __init__(self, order: int = 7):
        if order < 3:
            raise ValueError("Order must be >= 3")
        self.order = order
        self.d = (order - 1) // 2       # d = 1 pour ordre 3
        self.max_keys = 2 * self.d      # nombre max de clés par nœud
        self.min_keys = self.d
        self.root = BTreeNode(leaf=True)

    # ============================================================
    # RECHERCHE
    # ============================================================
    def search(self, k: int, node: Optional[BTreeNode] = None) -> Optional[Tuple[BTreeNode, int]]:
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and k > node.keys[i]:
            i += 1
        if i < len(node.keys) and node.keys[i] == k:
            return node, i
        if node.leaf:
            return None
        return self.search(k, node.children[i])

    # ============================================================
    # INSERTION (post-insert split)
    # ============================================================
    def insert(self, key: int):
        node = self.root
        self._insert_non_full(node, key)

        # si la racine déborde
        if len(self.root.keys) > self.max_keys:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self.root)
            self.root.parent = new_root
            self.root = new_root
            self._split_child(new_root, 0)

    def _insert_non_full(self, node: BTreeNode, key: int):
        if node.leaf:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node.keys.insert(i, key)

            if len(node.keys) > self.max_keys:
                self._handle_split_up(node)
            return

        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        child = node.children[i]
        self._insert_non_full(child, key)

    def _handle_split_up(self, node: BTreeNode):
        if node == self.root:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(node)
            node.parent = new_root
            self.root = new_root
            self._split_child(new_root, 0)
            return

        parent = node.parent
        index = parent.children.index(node)
        self._split_child(parent, index)

        if len(parent.keys) > self.max_keys:
            self._handle_split_up(parent)

    def _split_child(self, parent: BTreeNode, i: int):
        full = parent.children[i]
        mid = len(full.keys) // 2
        median = full.keys[mid]

        new_node = BTreeNode(leaf=full.leaf)
        new_node.parent = parent

        new_node.keys = full.keys[mid + 1:]
        full.keys = full.keys[:mid]

        if not full.leaf:
            new_node.children = full.children[mid + 1:]
            for c in new_node.children:
                c.parent = new_node
            full.children = full.children[:mid + 1]

        parent.keys.insert(i, median)
        parent.children.insert(i + 1, new_node)

    # ============================================================
    # SUPPRESSION (améliorée)
    # ============================================================
    def delete(self, k: int):
        if not self.root:
            return

        self._delete_internal(self.root, k)

        if self.root and len(self.root.keys) == 0:
            if self.root.leaf:
                self.root = None
            else:
                self.root = self.root.children[0]
                self.root.parent = None

    def _delete_internal(self, node: BTreeNode, k: int):
        idx = self._find_key_index(node, k)

        # === CAS 1 : clé trouvée dans ce nœud ===
        if idx < len(node.keys) and node.keys[idx] == k:
            if node.leaf:
                node.keys.pop(idx)
                return

            left_child = node.children[idx]
            right_child = node.children[idx + 1]

            if len(left_child.keys) > self.min_keys:
                pred = self._get_predecessor(left_child)
                node.keys[idx] = pred
                self._delete_internal(left_child, pred)
                return

            if len(right_child.keys) > self.min_keys:
                succ = self._get_successor(right_child)
                node.keys[idx] = succ
                self._delete_internal(right_child, succ)
                return

            self._merge(node, idx)
            self._delete_internal(node.children[idx], k)
            return

        # === CAS 2 : clé non trouvée ===
        if node.leaf:
            return

        if idx >= len(node.children):
            idx = len(node.children) - 1

        child = node.children[idx]

        if len(child.keys) <= self.min_keys:
            if idx > 0 and len(node.children[idx - 1].keys) > self.min_keys:
                self._borrow_from_prev(node, idx)
            elif idx < len(node.children) - 1 and len(node.children[idx + 1].keys) > self.min_keys:
                self._borrow_from_next(node, idx)
            else:
                if idx < len(node.children) - 1:
                    self._merge(node, idx)
                else:
                    self._merge(node, idx - 1)
                    idx -= 1
                child = node.children[idx]

        self._delete_internal(child, k)

    # ============================================================
    # OUTILS DE SUPPRESSION
    # ============================================================
    def _find_key_index(self, node: BTreeNode, k: int) -> int:
        idx = 0
        while idx < len(node.keys) and node.keys[idx] < k:
            idx += 1
        return idx

    def _get_predecessor(self, node: BTreeNode) -> int:
        cur = node
        while not cur.leaf:
            cur = cur.children[-1]
        return cur.keys[-1]

    def _get_successor(self, node: BTreeNode) -> int:
        cur = node
        while not cur.leaf:
            cur = cur.children[0]
        return cur.keys[0]

    def _borrow_from_prev(self, parent: BTreeNode, idx: int):
        child = parent.children[idx]
        sibling = parent.children[idx - 1]
        child.keys.insert(0, parent.keys[idx - 1])
        if not sibling.leaf:
            moved = sibling.children.pop()
            moved.parent = child
            child.children.insert(0, moved)
        parent.keys[idx - 1] = sibling.keys.pop()

    def _borrow_from_next(self, parent: BTreeNode, idx: int):
        child = parent.children[idx]
        sibling = parent.children[idx + 1]
        child.keys.append(parent.keys[idx])
        if not sibling.leaf:
            moved = sibling.children.pop(0)
            moved.parent = child
            child.children.append(moved)
        parent.keys[idx] = sibling.keys.pop(0)

    def _merge(self, parent: BTreeNode, idx: int):
        child = parent.children[idx]
        sibling = parent.children[idx + 1]
        child.keys.append(parent.keys[idx])
        child.keys.extend(sibling.keys)
        if not child.leaf:
            for c in sibling.children:
                c.parent = child
            child.children.extend(sibling.children)
        parent.keys.pop(idx)
        parent.children.pop(idx + 1)

    # ============================================================
    # DEBUG
    # ============================================================
    def print_tree(self, node: Optional[BTreeNode] = None, lvl: int = 0):
        if node is None:
            node = self.root
        if node is None:
            print("(arbre vide)")
            return
        print("  " * lvl + str(node.keys))
        if not node.leaf:
            for c in node.children:
                self.print_tree(c, lvl + 1)


# ============================================================
# TEST DE VALIDATION
# ============================================================

# Exemple simple
if __name__ == "__main__":
    b = bTree(order=5)
    for x in [10, 20, 5, 6, 12, 30, 7, 17]:
        b.insert(x)

    print("Arbre initial :")
    b.print_tree()

    print("\nSuppression de 6, 7, 12 :")
    for k in [6, 7, 12]:
        b.delete(k)
        b.print_tree()
