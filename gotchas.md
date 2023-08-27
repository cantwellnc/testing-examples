# Gotchas
- Mixing fixtures + strategies
    1. use kwargs for strategies in `@given`; don't rely on positional arguments! This is a style + organizational thing. Makes it easier to keep track of what data is coming from hypothesis vs your fixtures. 
    2. The scope of a fixture **cannot** be `"function"`. Hypothesis will only run your fixture *a single time* rather than running the fixture every time the test is run (both during example generation + shrinking). See [here](https://hypothesis.works/articles/hypothesis-pytest-fixtures/) for more details. 
    3. If you're putting random values from a strategy **into** a fixture, the only way I was able to get this to work was by making the fixture itself not take any params + instead return an inner function that takes the params you want. Then in your test (once you've requested the strategy using `@given`) you can request the fixture + pass the strategy in when the test runs (ex: `my_fixture(my_strategy)`). 
    4. This goes back to point 2, but it's worth stating separately: IF YOU ARE USING THE PYTEST MOCKER FIXTURE (from pytest_mock), you must use the **module_mocker** or **session_mocker**. You can import these specifically from pytest_mock. 

- How to use `composite` and `builds`, and the differences between them. 
    - the pii tag strategy is a good example. I wanted to generate a dict like `{"Key": "pii", "Value": "true | false"}`, but the choice of `"true"` or `"false"` should be random. 
    - A way to get such a value is to use the `.map()` method that comes with all strategies in hypothesis. 
    ```python
        str_bool = st.boolean.map(lambda x: str(x).lower())
    ```
    - When I plugged this into my bigger tags object, I did it like: 
    ```python
        pii_tag = st.just({"Key": "pii", "Value": str_bool()})
    ```
    - This ended up producing results like `{"Key": "pii", "Value": boolean.map(lambda x: str(x).lower())}`. Hypothesis is **not** able to evaluate the str_bool strategy! So what happened? 
    - What I actually needed to do was pass a **specific** value to `st.just`, rather than another strategy. If you're inside a composite strategy, you get a function called `draw` that allows you to draw values from a strategy + then build something using those values. 
    ```python
        str_bool = draw(st.boolean.map(lambda x: str(x).lower()))
        pii_tag = st.just({"Key": "pii", "Value": str_bool()})
    ```
    - THIS produces the expected result. 
- When to use each: 
    - `st.builds` is useful when you have a class that you want to fill with data or arguments that do not have any interdependence on each other. It is a very powerful tool!
    - `st.composite` is even more powerful: it allows you to express dependencies between arguments (via how you create your data structures, or using `assume`). 
        - The real power is that you can GENERATE your data in a way that captures the structure you want, rather than having to generate a bunch of stuff that may not fit your constraints + then filter your results after you've done all that generation work. 
    - while `st.builds` can technically do this, as mentioned above, it is very inefficient bc you can only filter AFTER generation, rather than building your constraints into your generation process (so that all the examples you generate fit your constraints). See [here](https://hypothesis.works/articles/generating-the-right-data/) for more details. 

- There is a strategy for random functions, `st.functions`. You can provide a type signature or an example lambda + Hypothesis will generate functions of that type. Usually, if it finds a failing example function, it will present it to you + you can see what it does. However, if your functions never actually get called, then example generation kinda breaks. 
    - this can result in a failing output being presented as `lambda: unknown`. 

- I refactored my random_tags_object strategy + it broke some tests! I expected the call-not-assert pattern to catch one of the bugs (assuming a non-empty TagSet) in has_pii_content, but it never did. I needed to write two additional tests (one with no pii presesnt (didn't catch it) and one where the object always has pii). The situation where a tag always has pii is what caught the bug, but it a more complicated way than I wanted. 
    - the reason for all this rigamarole is bc I accidentally built random_tags_object in such a way that it always returns a **NON-EMPTY LIST OF TAGS**. Hence, I literally could not generate data to catch the bug. whoops! 
- moral of the story here is to be very very careful when constructing generators for data, since you might accidentally rule out edge cases you actually want to test!
    
    


