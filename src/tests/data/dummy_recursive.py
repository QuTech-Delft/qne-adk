def main(app_config=None, q1=0, q2=2):
    q1 = q1 * 3
    return the_real_return(q1)

def the_real_return(x):
    if x:
        return {
            "col": "col_outcomes",
            "square": "square",
            "string": "yo",
            "number": 2
        }

    return {
            "col1": "col_outcomes",
            "square1": "square",
            "string1": "yo",
        }

if __name__ == "__main__":
    main()
