# testing-examples
exploring different tools for testing in Python, particularly property-based testing. 

basic example is exploring a purposefully flawed string-reversal algorithm in `src/reversal.py` and `src/tests/reversal_test
- note: I claim that the properties we list uniquely characterize a string reversal algorithm; this is not true! we need a properties 
that asserts that the indices move in the appropriate way. Otherwise, a Caesar cipher with a shift of 13 also satisfies these properties. 

more advanced exmaple that incorporates mocking + a fake usecase of detecting PII (Personally Identifiable Information) in an AWS account
is in `src/main.py` and `src/tests/main_property_based_test.py`. 

there are also some examples of other testing tools (snapshot testing w syrupy). feel free to explore those too!
