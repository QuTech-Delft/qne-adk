def main(app_config=None, q1=0, q2=2):
    q1 = q1 * 3
    if q1 > 9:
        return {
            "first_return": 1,
            "col": "col_outcomes",
            "square": "square",
            "string": "yo",
            "number": 2
        }

    return the_return(q1)


def the_return(y):
    if y > 20:
        return {
            "col": "some col",
            "square": "some 2",
            "string": "some 3",
            "number": 5
        }

    return {
            "col1": "another col",
            "square1": "circle",
            "string1": "hi",
        }


if __name__ == "__main__":
    main()
