import random
import itertools

class Solver:
	def __init__(self, problem):
		self.solution = []
		self.problem = problem

	def solve(self, **kwargs):
		pass


class ExhaustiveSolver(Solver):
	def solve(self, **kwargs):
		for subset in self.subsets(self.problem.graph.vertexes):
			edges_covered = 0
			visited_edges = []
			for vertex in subset:
				inc_edges = self.problem.graph.get_incident_edges(vertex)
				for edge in inc_edges:
					if edge not in visited_edges:
						visited_edges.append(edge)
						edges_covered += 1

			if edges_covered == self.problem.E:
				if not self.solution or (len(subset) < len(self.solution)):
					self.solution = subset

		return self.solution 

	def subsets(self, lst):
		res = []
		for i in range(len(lst)):
			res.extend(list(itertools.combinations(lst, i)))
		return res

class RandomizedSolver(Solver):
	def solve(self, **kwargs):
		MAX_ITERS = kwargs.get("iters") or 1000
		computed_solutions = []
		best = []
		cur_size = 1
		size_cnt = 0
		for i in range(MAX_ITERS):
			rand_mvc = self.get_random_mvc(min(cur_size, self.problem.V), computed_solutions)
			size_cnt += 1
			if not rand_mvc:
				if size_cnt == self.problem.V:
					cur_size += 1
					size_cnt = 0
			else:
				computed_solutions.append(rand_mvc)
				if not best:
					best = rand_mvc

				elif len(rand_mvc) < len(best):
					best = rand_mvc
		return best

	def get_random_mvc(self, size, computed_solutions):
		starting_vertex = random.choice(self.problem.graph.vertexes)
		mvc = [starting_vertex]
		while (len(mvc) < size):

			nxt = self.choose_next_vertex(mvc)
			if not nxt:
				if self.is_vertex_cover(mvc):
					return mvc
				else:
					return None 

			mvc.append(nxt)

		if self.is_vertex_cover(mvc) and set(mvc) not in computed_solutions:
			return mvc
		return None

	def total_neighbors(self, subset):
		t = []
		for v in subset:
			neighbors = self.problem.graph.get_neighbors(v)
			t += [elem for elem in neighbors if elem not in subset and elem not in t]
		return t

	def choose_next_vertex(self, subset):
		neighbors = self.total_neighbors(subset)
		available = [e for e in neighbors]

		if not available:
			return None
		
		return random.choice(available)

	def is_vertex_cover(self, subset):
		for edge in self.problem.graph.edges:
			u, v = edge.get_vertexes()
			if not (u in subset or v in subset):
				return False
		return True
			
class GreedySolver(Solver):
	def solve(self, **kwargs):
		C = []
		best_candidates = [v for v in self.problem.graph.vertexes]
		best_candidates.remove(min(best_candidates, key=lambda v: self.score(C, v)))
		while True:
			if self.is_vertex_cover(C) and self.is_connected(C):
				break

			v = random.choice(best_candidates)
			C.append(v)
			best_candidates = [v for v in self.total_neighbors(C)]
			best_candidates.remove(min(best_candidates, key=lambda v: self.score(C, v)))
		return C

	def is_vertex_cover(self, subset):
		for edge in self.problem.graph.edges:
			u, v = edge.get_vertexes()
			if not (u in subset or v in subset):
				return False
		return True

	def is_connected(self, subset):
		if not subset:
			return False
		visited = self.neighbor_search(subset[0], [])
		if len(visited) == self.problem.V:
			return True
		return False

	def neighbor_search(self, vertex, visited):
		visited.append(vertex)

		for n in self.problem.graph.get_neighbors(vertex):
			if n not in visited:
				self.neighbor_search(n, visited)
		return visited
		

	def edges_covered(self, subset):
		edges = []
		for v in subset:
			for e in self.problem.graph.get_incident_edges(v):
				if e not in edges:
					edges.append(e)
		return edges
	
	def solution_cost(self, subset):
		return len([e for e in self.problem.graph.edges if e not in self.edges_covered(subset)])
	
	def score(self, subset, vertex):
		return self.solution_cost(subset) - self.solution_cost(subset + [vertex])

	def total_neighbors(self, subset):
		t = []
		for v in subset:
			neighbors = self.problem.graph.get_neighbors(v)
			t += [elem for elem in neighbors if elem not in subset and elem not in t]
		return t

