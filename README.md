# Fréchet Matching Queries

[query_example]: query_example.png
[report]: https://github.com/ermel272/frechet-matching-queries/blob/master/report.pdf

The purpose of this project is to implement a few of the data structures and algorithms produced in the paper 
**Fast Algorithms for Approximate Fréchet Matching Queries in Geometric Trees** by Michiel Smid and Joachim
Gudmundsson. The project [report][report] discusses some of the concepts used and implementation challenges faced,
as well as provides some empirical evidence hinting at the practical performance of the data structures.

The primary result attained in Smid and Gudmundsson's paper is the following. Given a geometric tree T, we wish to 
preprocess it such that, given a polygonal query path P, we can efficiently determine whether or not T contains a path
P' such that δ<sub>F</sub>(P, P') ≤ 3(1 + ε)Δ, where Δ and ε are predetermined constants. Please see below for
a visual example of such a query.

![query_example]
