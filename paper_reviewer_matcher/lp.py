import numpy as np
from tqdm.auto import tqdm
from scipy.sparse import coo_matrix
from ortools.linear_solver import pywraplp

__all__ = ["linprog"]

def linprog(f, A, b):
    """
    Solve the following linear programming problem
            maximize_x (f.T).dot(x)
            subject to A.dot(x) <= b
    where   A is a sparse matrix (coo_matrix)
            f is column vector of cost function associated with variable
            b is column vector
    """

    # flatten the variable
    f = f.ravel()
    b = b.ravel()

    solver = pywraplp.Solver('SolveReviewerAssignment',
                             pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

    infinity = solver.Infinity()
    n, m = A.shape
    x = [[]] * m
    c = [0] * n

    print("Setting up variables...")
    for j in tqdm(range(m)):
        x[j] = solver.NumVar(-infinity, infinity, 'x_%u' % j)

    # state objective function
    print("Setting up objective function...")
    objective = solver.Objective()
    for j in tqdm(range(m)):
        objective.SetCoefficient(x[j], f[j])
    objective.SetMaximization()

    # state the constraints
    print("Setting up constraints...")
    for i in tqdm(range(n)):
        c[i] = solver.Constraint(-infinity, int(b[i]))
        for j in A.col[A.row == i]:
            c[i].SetCoefficient(x[j], A.data[np.logical_and(A.row == i, A.col == j)][0])

    result_status = solver.Solve()
    if result_status != 0:
        print("The final solution might not converged")

    x_sol = np.array([x_tmp.SolutionValue() for x_tmp in x])

    return {'x': x_sol, 'status': result_status}


def test_example():
    """
    Solves example problem from http://www.vitutor.com/alg/linear_programming/example_programming.html
        f(x,y)= 50x + 40y
    subject to:
        2x+3y <= 1500
        2x + y <= 1000
        x >= 0 -> -x <= 0
        y >= 0 -> -y <= 0
    """
    f = np.array([50, 40], dtype=float)
    A = np.array([[ 2, 3],
                  [ 2, 1],
                  [-1, 0],
                  [ 0, -1]], dtype=float)
    C = np.array([1500, 1000, 0, 0])
    x_sol = linprog(f, coo_matrix(A), C)
    print('Example Problem:')
    print('maximize_x\t 50x + 40y')
    print('s.t.\t\t 2x+3y <= 1500, 2x + y <= 1000, x >= 0, y >= 0')
    print('Solution: (x, y) = ', x_sol)


if __name__ == '__main__':
    test_example()
