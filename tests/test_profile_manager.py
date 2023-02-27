from squirrels import profile_manager as pm


def test_profile_manager():
    profile_name = 'unit-test'
    profile1 = pm.Profile(profile_name)
    profile2 = pm.Profile(profile_name)
    profile1.delete()
    assert(profile_name not in pm.get_profiles())

    expecteds = [
        {'dialect': 'sqlite', 'conn_url': 'url1', 'username': 'user1', 'password': 'pass1'},
        {'dialect': 'mysql', 'conn_url': 'url2', 'username': 'user2', 'password': 'pass2'}
    ]
    
    for expected in expecteds:
        profile1.set(**expected)
        assert(profile1.get() == expected)
        assert(profile2.get() == expected)
        assert(profile_name in pm.get_profiles())

    profile2.delete()
    assert(profile1.get() == {})
    assert(profile2.get() == {})
    assert(profile_name not in pm.get_profiles())
