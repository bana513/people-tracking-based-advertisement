def get_advertisement(total_people, moving_in, moving_out, moving_left, moving_right):
    if total_people>=4:
        return 'random.jpg', 'total_people>=4'
    return None, 'No satisfactory condition'
