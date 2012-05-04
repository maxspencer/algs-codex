'''

	An implementation of the van Emde Boas tree data structure.
	
	vEB trees have O(lglgn) asymtotic complexity for all operations, provided
	the size of the universe of keys is known and there are no duplicate keys.
	They work on the principle of being a 'recursive datastructure', where a vEB
	tree with a total of u leaves will have sqrt(u) children of the root and
	each of those children will have sqrt(sqrt(u)) children and so on until the
	nodes have a universe size of 2.
	
	More details can be found in 'Introduction to Algorithms', Cormen et. al.
	and that text has been a guide for me in writing this implementation.
	
'''
import math;

def high(x, u):
	'''Returns the value of the "high bits" of the value x, in universe size u.
	'''
	ru = math.floor(math.sqrt(u))
	return math.floor(x / ru)

def low(x, u):
	'''Returns the value of the "low bits" of the value x, in universe size u.
	'''
	ru = math.floor(math.sqrt(u))
	return x % ru

def index(x, y, u):
	'''Returns the original index of an element from its high and low bits, in 
	universe size u.
	'''
	ru = math.floor(math.sqrt(u))
	return (x * ru) + y

# Note the identity x = index(high(x, u), low(x, u), u).

class ProtoVEBTree(object):
	'''A proto vEB tree (node) which may be part of the cluster of another node.
	
	A proto vEB Tree is a step towards the full vEB tree and the desired 
	O(lglgn) asymtotic complexity for all operations. It is a recursive
	datastructure, but needs further optimisation. It's main purpose is to aid
	in understanding vEB trees and the motivation for their features.
	'''
	def __init__(self, u):
		'''Create an empty proto vEB tree with universe of size u and this being
		the root node.
		
		NB:	Currently only values of u which are allowed are 2^(2^k) where k is
		a positive integer. Use of any other value will result in undefined 
		behaviour.
		'''
		if u == 2:
			# Base case.
			self.u = 2
			self.A = [False, False]
		else:
			# General case.
			self.u = u
			self.ru = math.floor(math.sqrt(u))
			self.summary = ProtoVEBTree(self.ru)
			self.cluster = list()
			for _ in range(self.ru):
				self.cluster.append(ProtoVEBTree(self.ru))
	
	def __str__(self):
		'''Return a unique string to identify this node.
		'''
		# Return the memory address.
		return str(self)[33:-1]
	
	def insert(self, x):
		'''Inserts an item x into the proto vEB tree.
		'''
		if self.u == 2:
			self.A[x] = True
		else:
			self.cluster[high(x, self.u)].insert(low(x, self.u))
			self.summary.insert(high(x, self.u))
	
	def delete(self, x):
		'''Removes an element x from a proto vEB tree if it is present.
		
		True is returned if any parent of this node needs to update its summary.
		'''
		if self.u == 2:
			self.A[x] = False
			return not (self.A[0] or self.A[1])
			# So return True in the case where now both items in this leaf
			# are False.
		elif self.cluster[high(x, self.u)].delete(low(x, self.u)):
			# If a deletion from a child is saying this node's summary must be
			# updated then forward the result to continue the "bubbling-up" of
			# this change if necessary.
			return self.summary.delete(high(x, self.u))
		else:
			return False
	
	def member(self, x):
		'''Returns True if x is present in this proto vEB tree, or False
		otherwise.
		'''
		if self.u == 2:
			return self.A[x]
		else:
			return self.cluster[high(x, self.u)].member(low(x, self.u))
			
	def minimum(self):
		'''Return the value of the minimum item in this proto vEB tree, or None
		if it is empty.
		'''
		if self.u == 2:
			if self.A[0] == 1:
				return 0
			elif self.A[1] == 1:
				return 1
			else
				return None
		else:
			min_cluster = self.summary.minimum()
			if min_cluster != None:
				offset = self.cluster[min_cluster].minimum()
				return index(min_cluster, offset, self.u)
			else
				return None
	
	def maximum(self):
		'''Return the value of the maximum item in this proto vEB tree, or None
		if it is empty.
		'''
		if self.u == 2:
			if self.A[1] == 1:
				return 1
			elif self.A[0] == 1:
				return 0
			else
				return None
		else:
			max_cluster = self.summary.maximum()
			if max_cluster != None:
				offset = self.cluster[max_cluster].maximum()
				return index(max_cluster, offset, self.u)
			else
				return None
		
	def predecessor(self, x):
		'''Returns the maximum value less than x in this proto vEB tree, or None
		of no such value exists.
		
		TODO
		'''
		if u == 2:
			if (x == 1) and (self.A[0] == 1):
				return 0
			else:
				return None
		else:
			pred_in_cluster = self.cluster[high(x, self.u)].predecessor(low(x, self.u))
			if pred_in_cluster != None:
				return index(high(x, self.u), pred_in_cluster, self.u)
			else:
				# In a different cluster
				pred_cluster = self.summary.predecessor(high(x, self.u))
				if pred_cluster != None:
					offset = self.cluster[pred_cluster].maximum()
					return index(pred_cluster, offset, self.u)
				else:
					return None
		
	def successor(self, x):
		'''Returns the minimum value greater than x in this proto vEB tree, or
		None of no such value exists.
		'''
		pass
	
	def to_DOT(self, wrap = False, summary = False, glabel = None):
		'''Output a string in the DOT language which describes this proto vEB 
		tree.
		'''
		node = "node" + str(self)
		# Write string for node record.		
		node_options = "fontsize = 12, color = black"
		if summary:
			node_options += ", fillcolor = gray, style = filled"
		
		if self.u == 2:
			label = "{ <u>" + str(self.u) + " " +\
					"| <A0>" + str(int(self.A[0])) + " " +\
					"| <A1>" + str(int(self.A[1])) + " }"
		else:
			label = "<u>" + str(self.u) + " | <summary>summary | { cluster | { <c0>"
			for i in range(1, len(self.cluster)):
				label += " | <c" + str(i) + ">"
			label += " } }"
		
		record = node + "[" + node_options + ", label = \"" + label + "\"]\n"
		
		# Write string for any edges.
		if self.u > 2:
			edges = "\"" + node + "\":summary -> " +\
					"\"node" + str(self.summary) + "\";\n"
			for i in range(self.ru):
				c = self.cluster[i];
				edges += "\"" + node + "\":c" + str(i) + " -> " +\
						 "\"node" + str(c) + "\";\n"
			
		# Final result.
		if self.u == 2:
			result = record
		else:
			result = record + edges
			# Recurse into summary and cluster nodes.
			result += self.summary.to_DOT(False, True);
			for c in self.cluster:
				result += c.to_DOT();
		
		# Perhaps wrap with the outer curly braces.
		if wrap:
			if glabel:
				result = "[labelloc = t, label = \"" + glabel + "\"]\n" + result
			result = "digraph g {\nnode [shape = record]\n" + result + "}"
		
		return result

class VEBTree(object):
	'''A vEB tree (node) which may be part of the cluster of another node.
	
	A node stores u, the universe size of the node. summary, a pointer to 
	another vEB tree which summarizes the contents of this node's cluster.
	cluster, which is an array of sqrt(u) items which are pointers to child 
	VEBTree's each with a universe size of sqrt(u). min, the value of the
	smallest key in the tree (this does not also appear in clusters). max, the
	value of the maximum item in the tree (also appears in clusters).
	'''
	def __init__(self, u):
		'''Create an empty vEB tree with universe of size u and this being the
		root node.
		
		NB:	Currently only values of u which are allowed are 2^(2^k) where k is
		a positive integer. Use of any other value will result in undefined 
		behaviour.
		'''
		self.min = self.max = None
		if(u == 2):
			# Base case.
			self.u = 2
		else:
			self.u = u
			self.ru = math.floor(math.sqrt(u))
			self.summary = VEBTree(self.ru)
			self.cluster = list()
			for i in range(self.ru):
				self.cluster.append(VEBTree(self.ru));
	
	def __str__(self):
		'''Return a unique string to identify this node.
		'''
		# Return the memory address.
		return str(self)[32:-1]
	
	def insert(self, x):
		'''Inserts key x into the vEB tree.
		'''
		if self.min == None:
			self.min = self.max = x
		else:
			if x < self.min:
				# Swap x and the current min.
				t = self.min
				self.min = x
				x = t
				del t
			if self.u > 2:
				if self.cluster[high(x, self.u)].minimum() is None:
					# If the cluster for x has no minimum it is empty and so we 
					# need to update the summary to say there is some thing in 
					# it.
					self.summary.insert(high(x, self.u))
				# Insert the x into its cluster.
				self.cluster[high(x, self.u)].insert(low(x, self.u))
			if x > self.max:
				# Case where node has u = 2 and only one value stored
				# (min = max).
				self.max = x
					
	def delete(self, x):
		'''TODO
		'''
		pass
	
	def member(self, x):
		'''Returns True is x is a key in this vEB tree or false otherwise.
		'''
		if (x is self.min) or (x is self.max):
			return True
		elif self.u is 2:
			return False
		else:
			return self.cluster[high(x, self.u)].member(low(x, self.u))
	
	def minimum(self):
		'''Return the minimum element of the tree.
		'''
		return self.min
	
	def maximum(self):
		'''Return the maximum element of the tree.
		'''
		return self.max
	
	def predecessor(self, x):
		'''Returns the next lowest key stored in the vEB tree below x, or None
		if no such key exists.
		'''
		if self.u == 2:
			# Base case.
			if (self.min == 0) and (x == 1):
				return 0
			else:
				return None
		elif (self.max != None) and (x > self.max):
			return self.max
		else:
			# General case.
			min_in_cluster = self.cluster[high(x, self.u)].minimum()
			if (min_in_cluster != None) and (low(x, self.u) > min_in_cluster):
				# There must be some predecessor in this cluster, if only the
				# min itself.
				offset = self.cluster[high(x, self.u)].predecessor(low(x, self.u))
				return self.index(high(x, self.u), offset)
			else:
				# Otherwise find the non-empty cluster predecessor
				pred_cluster = self.summary.predecessor(high(x, self.u))
				# ..and look for the maximum in there.
				if pred_cluster == None:
					# Extra case, predecessor might be the min of self because
					# unlike max's min's are no stored in the clusters.
					if (self.min != None) and (self.min < x):
						return self.min
					else:
						return None
				else:
					offset = self.cluster[pred_cluster].maximum()
					return self.index(pred_cluster, offset)
	
	def successor(self, x):
		'''Returns the next highest key stored in the vEB tree above x, or None
		if no such key exists.
		'''
		if self.u == 2:
			# Base case.
			if x == 0 and self.max == 1:
				return 1
			else:
				return None
		elif (self.min != None) and (x < self.min):
			return self.min
		else:
			# General case.
			max_in_cluster = self.cluster[high(x, self.u)].maximum()
			if (max_in_cluster != None) and (low(x, self.u) < max_in_cluster):
				# There must be some successor (at least the max) in the same 
				# cluster as k, so go and find it in there!
				offset = self.cluster[high(x, self.u)].successor(low(x, self.u))
				return self.index(high(x, self.u), offset)
			else:
				# Otherwise, find the next cluster with something in it.
				succ_cluster = self.summary.successor(high(x, self.u))
				# ...and look for the minimum in there.
				if succ_cluster == None:
					return None
				else:
					offset = self.cluster[succ_cluster].minimum()
					return self.index(succ_cluster, offset)
	
	def to_DOT(self, wrap = False, summary = False, glabel = None):
		'''Output a string in the DOT language which describes this vEB tree.
		'''
		node = "node" + str(self)
		# Write string for node record.		
		node_options = "fontsize = 12, color = black"
		if summary:
			node_options += ", fillcolor = gray, style = filled"
		
		if self.u == 2:
			label = "{ <u>" + str(self.u) + " " +\
					"| <min>" + str(self.min) + " " +\
					"| <max>" + str(self.max) + " }"
		else:
			label = "<u>" + str(self.u) + " | " +\
					"<min>" + str(self.min) + " | " +\
					"<max>" + str(self.max) + " | "
					"<summary>summary | { cluster | { <c0>"
			for i in range(1, len(self.cluster)):
				label += " | <c" + str(i) + ">"
			label += " } }"
		
		record = node + "[" + node_options + ", label = \"" + label + "\"]\n"
		
		# Write string for any edges.
		if self.u > 2:
			edges = "\"" + node + "\":summary -> " +\
					"\"node" + str(self.summary) + "\";\n"
			for i in range(self.ru):
				c = self.cluster[i];
				edges += "\"" + node + "\":c" + str(i) + " -> " +\
						 "\"node" + str(c) + "\";\n"
			
		# Final result.
		if self.u == 2:
			result = record
		else:
			result = record + edges
			# Recurse into summary and cluster nodes.
			result += self.summary.to_DOT(False, True);
			for c in self.cluster:
				result += c.to_DOT();
		
		# Perhaps wrap with the outer curly braces.
		if wrap:
			if glabel:
				result = "[labelloc = t, label = \"" + glabel + "\"]\n" + result
			result = "digraph g {\nnode [shape = record]\n" + result + "}"
		
		return result

if __name__ == "__main__":
	test_data = {2, 3, 4, 5, 7, 10}
	test_size = 16
	test_tree = ProtoVEBTree(test_size)
	print(test_tree.to_DOT(True, False, "Empty"))
	for d in test_data:
		test_tree.insert(d)
	print(test_tree.to_DOT(True, False, "Data inserted"))
	for d in test_data:
		test_tree.delete(d)
		print(test_tree.to_DOT(True, False, "Removed " + str(d)))
