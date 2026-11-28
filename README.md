# Cmpt360-Project
Project for Cmpt360

Requires Python 3.8 or newer
Only the standard library is required

Files
baseline.py -- contains the brute-force baseline algorithm, the fits helper, and the initial fixed thirds attempt.
fastest.py -- contains both dynamic programming approaches:
    -faster(S) -- examines every pair of split points and uses a three way longest common subsequence dynamic program
    -fastest(S) -- improves the split based approach with symbol count pruning, an upper bound for each split and a length only DP using rolling layers. It reconstructs the subsequence for the winning split.


Running:
Running the baseline attempt by calling 
    ~ python baseline.py
This runs the test cases from first_try() and baseline()

Running the fasterAlgo attempt by calling
    ~ python fasterAlgo.py
This runs the test cases from faster() and fastest()

The test strings include:
"aaabbbccc"
"atcgtatgcatgca"
"abcabcab"
"abcabcabcxyzxyzxyz"
"aaa"
