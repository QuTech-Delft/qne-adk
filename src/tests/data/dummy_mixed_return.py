def main(app_config=None, q1=0, q2=2):
    some_var = {'key': 'value'}

    if q1 > 9:
        return {
            "dict_return": 1,
        }

    return some_var


if __name__ == "__main__":
    main()
