'''

    An implementation of the Fibonacci Heap datastructure and the other 
    data structures it uses in its construction.

    The motivation for the Fibonacci Heap was improving the asymptotic running
    time of the Dijkstra algorithm which involves operating on nodes in a
    priority queue. The cost of Dijkstra becomes directly proportional to the
    running cost of decreaseKey() for a connected graph. With a Fibonacci Heap,
    a lot of the "tidying up" work is done by extractMin() which retains O(lgn)
    amortized cost and decreaseKey() has only constant cost!

    For a detailed discussion of the Fibonacci Heap see Introduction to
    Algorithms, Cormen et al. Chapter 19.
    
    
'''

from item import Item

class CircularDLL(object):
    '''A circular doubly-linked list. Its elements must implement the base Item
    interface.
    '''
    def __init__(self, init_items = []):
        '''Initialise the circular doubly-linked list either as empty or with
        some iterable of Items as its initial contents.
        '''
        if(len(init_items) == 0): # Empty
            self.start = None
        else: # General
            # Loop the ends around
            init_items[0].left = init_items[-1]
            init_items[-1].right = init_items[0]
            # Make all the normal links
            prev = init_items[0]
            for item in init_items[1:]:
                prev.right = item
                item.left = prev
                prev = item
                
            self.start = init_items[0]
        # Set cur to point to start for now.
        # No longer used?
        self.cur = self.start
     
    def items(self):
        '''Returns a list of the items in the circular doubly-linked list.

        To do: It would be nice to make this into a Python iterator at some
        point. 
        '''
        result = list()
        if self.start:
            current = self.start
            while True:
                result.append(current)
                current = current.right
                if(current == self.start):
                    break
        return result        
    
    def __str__(self):
        '''Returns a sensible string representation of the circular
        double-linked list. 
        '''
        result = "["
        for item in self.items():
            result += str(item) + ', '
        result += "]"
        
        return result
    
    def insert(self, item):
        '''Insert an Item into the circular doubly-linked list.
        
        `item` will be inserted immediately before whichever Item `self.start`
        is pointing to.
        '''
        if self.start == None: # Empty list becoming a singleton.
            item.left = item.right = item
            self.start = item
        else: # General
            # Get neighbours
            leftNeighbour = self.start.left
            rightNeighbour = self.start
            # Make them friends
            leftNeighbour.right = item
            item.left = leftNeighbour
            item.right = rightNeighbour
            rightNeighbour.left = item       
            
    def merge(self, another):
        '''Merge this circular doubly-linked list with another one.
        
        The two lists will be joined by splitting both lists before the items
        which their `start` pointers point to and splicing the relevent
        pointers together at this point. 
        '''
        if self.start == None: # This list is empty.
            # Merging with the other list is equivalent to just becoming that
            # list, so we make this list's `start` point to the `start` item in
            # the other list.
            self.start = another.start
        elif another.start == None:
            pass
        else: # General case, proceed in a similar manner as with 'insert'.
            # Get the items which need joining
            start1 = self.start
            end1 = self.start.left
            start2 = another.start
            end2 = another.start.left
            # Link 'em up!
            start1.left = end2
            end1.right = start2
            start2.left = end1
            end2.right = start1
            
    def delete(self, item):
        '''Remove an item from the circular doubly-linked list.

        Note: It is assumed the caller has a pointer to the `item` they wish to
        remove.

        Warning: The effect of attempting to delete an Item from a circular
        doubly-linked list of which it is not a member is undefined and is
        likely to cause errors.

        To do: Sort out the above issue.. i.e. Arrange for a nice exception to
        occur at no increase in asymptotic cost.
        '''
        if(item != item.left): # General
            leftNeighbour = item.left
            rightNeighbour = item.right
            # Link
            item.right.left = leftNeighbour
            item.left.right = rightNeighbour
            self.start = item.right
        else: # Singleton
            item.left = item.right = None
            self.start = None

class FibHeapHItem(Item):
    '''A subclass of the Item base class specifically for Items to go in
    FibHeaps, which have some extra member variables and methods.
    '''
    def __init__(self, *args, **kwargs):
        # Pass arguments straight to the superclass constructor.
        Item.__init__(self, *args, **kwargs)
        self.parent = None
        self.children = None # Will optionally get pointed to a CircularDLL.
        self.marked = False
        self.degree = 0
        
    def link(self, other):
        '''Link this FibHeapItem to another one.
        
        Linking means to make the `other` item a child of this one, unmarking
        it and incrementing this item's `degree` accordingly.
        '''
        if self.children:
            self.children.insert(other)
        else:
            self.children = CircularDLL([other])
        other.marked = False
        other.parent = self
        self.degree += 1
        
    def __str__(self):
        '''Print this FibHeapItem as a string which is in some way useful...
        '''
        t = '<FibHeapItem: key={!s}, payload={!r}, marked={!s}, degree={!s}>'
        return t.format(self.key, self.payload, self.marked, self.degree)

    def to_DOT(self):
        label = '{!s} : {!s} ({!s})\n({!s})'.format(
            self.key, 
            self.payload.id(), 
            self.id(), 
            self.degree)
        
        node_t = '  {!s} [label="{!s}"'
        node_t += self.marked ? ', fillcolor="lightgrey"]\n' : '];\n'
        
        result = node_t.format(self.id(), label)

        if self.parent:
            result += '  {!s} -- {!s};\n'.format(self.parent.id(), self.id())

        for c in self.children.items():
            result += c.to_DOT()

        return result

class FibHeap(object):
    '''A Fibonnacci Heap which implements the interface of a priority queue.
    '''
    def __init__(self, init_item = None):
        '''Inititalise the FibHeap, optionally with a starting item.
        '''
        if init_item:
            self.roots = CircularDLL([init_item])
            self.n = 1
        else:
            self.roots = CircularDLL()
            self.n - 0

        self.min = init_item # Either None or the single item.
            
    def __str__(self):
        '''A sensible string representation of the FibHeap.
        '''
        if self.n == 0:
            return '<FibHeap: Empty>'
        else:
            t = '<FibHeap: decendants={!s}, min={!s}, roots={!s}>'
            return t.format(self.n, self.min, self.roots)
    
    def to_DOT(self, label = None):
        result = 'graph G {\n  label="{!s}";\n'.format(label)
        for i in self.roots.items():
            result += i.to_DOT()
        result += '}'
        return result
            
    def insert(self, item):
        '''Insert an item into this heap.
        '''
        self.roots.insert(item)
        self.n += 1
        if self.min:
            if self.min.key > item.key:
                self.min = item
        else:
            self.min = item
            
    def merge(self, another):
        '''Merge this FibHeap with another one.
        '''
        self.roots.merge(another.roots)
        self.n += another.n
        if self.min.key > another.min.key:
            self.min = another.min
    
    def first(self):
        '''Return the first item (i.e. the item with the minimum key), without 
        removing it from the FibHeap.
        '''
        return self.min
    
    def extract_min(self):
        '''Remove and return the first item.
        '''
        # Get the current minimum item.
        cm = self.min
        if cm != None:
            # Reset the parent pointers and add all children to the roots
            if cm.children:
                for c in cm.children.items():
                    c.parent = None
                self.roots.merge(cm.children)
            # Remove min item from roots.
            self.roots.delete(cm)
            self.n -= 1
            # Check if the heap is now empty, if not consolidate it.
            if self.roots.start == None:
                self.min = None
            else:
                self.consolidate()
        
        # Return (now no longer) current min
        return cm
        
    def consolidate(self):
        '''Consolidate the FibHeap.
        
        This is a tidying up process which makes the heap thinner and taller
        and sets the new `min` pointer after an `extract_min` occurs.
        '''
        # Bunching pass:
        new_roots = dict()
        # For each item in the roots
        for item in self.roots.items():
            # Keep executing this loop until it does not have the same degree as
            # any other already processed root item.
            while item.degree in new_roots:
                other = new_roots.pop(item.degree)
                # Swap the other item and this item
                if other.key < item.key:
                    temp = other
                    other = item
                    item = temp
                # Make whichever is now other, and therefore has a higher key,
                # the child of item.
                item.link(other)
            # When we exit the while loop, put the item into its slot.
            new_roots[item.degree] = item
            
        # Reforming/new-minimum-finding pass
        self.min = None
        for item in new_roots.values():
            if self.min == None:
                self.roots = CircularDLL([item])
                self.min = item
            else:
                self.insert(item)
                self.n -= 1 # As each `insert` of this will be adding 1 to n
                            # when really they are existing items that are just
                            # being re-inserted.
        
    def delete(self, item):
        '''Delete an item from its FibHeap.

        Warning: The behaviour if you attempt to remove an Item from a FibHeap
        of which it is not a member is undefined and is likely to cause
        problems.

        To do: Fix the above issue by having it do something nice, but without
        significantly increasing the cost of the function.
        '''
        self.decrease_key(item, float('-inf'))
        self.extract_min()
        
    def decrease_key(self, item, new_key):
        '''Decrease the `key` to `new_key`.
        '''
        assert(new_key <= item.key)
        item.key = new_key
        if(item.parent and item.key < item.parent.key):
            self.cut(item)
        if item.key < self.min.key:
            self.min = item
    
    def cut2(self, x, y):
        # Unused?
        '''Exact implementation of cut from CLRS, pg519.
        '''
        y.children.delete(x)
        y.degree -= 1
        self.roots.insert(x)
        x.parent = None
        x.marked = False
        
    def cascading_cut(self, y):
        # Unused?
        '''CLRS, pg519.
        '''
        z = y.parent
        if z != None:
            if y.marked == False:
                y.marked == True
            else:
                self.cut2(y, z)
                self.cascading_cut(z) 
        
    def cut(self, item):
        '''Cut item from its `parent` and move it into the `roots` of the
        FibHeap.

        Note: This may cause a cascade of cuts if the parent is marked.
        '''
        p = item.parent
        if p != None:
            # `item` is not a root node.
            p.children.delete(item)
            p.degree -= 1
            item.parent = None
            item.marked = False
            self.roots.insert(item)
            if p.parent:
                # If `parent` is not a root node.
                if p.marked:
                    self.cut(p)
                else:
                    p.marked = True

if __name__ == '__main__':
    '''Some basic usage examples:
    '''
    # Make an empty instance of the CircularDLL.
    mylist = CircularDLL()
    print(mylist)
    # Merge it with some anonymous other one.
    mylist.merge(CircularDLL([Item(1), Item(0, 'hello world')]))
    print(mylist)
    # Insert an item.
    myitem = Item(42, 'my item')
    mylist.insert(myitem)
    print(mylist)
    # Delete the item before that one.
    mylist.delete(myitem.left)
    print(mylist)
