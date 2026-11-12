#A deliberately badly formatted file, for the formatting demo of session 8. Run `black formatting_demo/`
#(or commit it with the pre-commit hook installed) and look at `git diff`: black fixes the layout and nothing else.
import numpy as np
def utility(c,gamma = 2.0):
  '''CRRA utility, log utility for gamma = 1'''
  if gamma==1 :
      return np.log( c )
  return c**(1-gamma)/(1-gamma)
def bisect(f,lo,hi,tol = 1E-6):
    #find the root of f on [lo, hi] by bisection, f increasing
    while hi-lo>tol:
        mid=(lo+hi)/2
        if f(mid)<0: lo=mid
        else: hi=mid
    return (lo+hi)/2
grid = np.linspace(0,100,200)**2/100   ;   values = utility(grid+1)
upper = grid[len(grid)//2 :]
weights=[0.25,0.5,0.25]
root = bisect(lambda r:utility(1+r,gamma=2.0)-utility(1.02,gamma=2.0),0.0,0.1,1E-8)
summary = dict(root = root, utility_at_root = utility(1+root), mean_utility_on_grid = values.mean(), grid_points = len(grid), tolerance = 1E-8)
print('root %.6f, utility at the root %.6f' % (root,utility(1+root)))
