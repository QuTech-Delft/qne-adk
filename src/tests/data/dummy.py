def main(app_config=None, q1=0, q2=2):
    q1 = q1 * 3
    if q1 > q2:
        return {'Q1': q1}

    return {
            "table": 'table',
            "x_basis_count": 'x_basis_count',
            "z_basis_count": 'z_basis_count',
            "same_basis_count": 'same_basis_count',
            "outcome_comparison_count": 'outcome_comparison_count',
            "diff_outcome_count": 'diff_outcome_count',
            "qber": 'qber',
            "key_rate_potential": 'key_rate_potential',
            "raw_key": 'raw_key_text',
        }


if __name__ == "__main__":
    main()
