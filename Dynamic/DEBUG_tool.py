LEVEL = "NONE"# NONE, SIMPLE, DETAIL


def DEBUG_log(s,s_level ="SIMPLE"):
    if s_level =="VERY_DETAIL" and (LEVEL =="VERY_DETAIL"):
        print(s)
    elif s_level =="DETAIL" and (LEVEL =="DETAIL"or LEVEL=="VERY_DETAIL"):
        print(s)
    elif s_level =="SIMPLE" and (LEVEL =="DETAIL" or LEVEL=="SIMPLE" or LEVEL=="VERY_DETAIL"):
        print(s)


def DEBUG_log_tag(tag,s,s_level ="SIMPLE"):
    if s_level =="VERY_DETAIL" and (LEVEL =="VERY_DETAIL"):
        print(tag)
        print(s)
    elif s_level =="DETAIL" and (LEVEL =="DETAIL"or LEVEL=="VERY_DETAIL"):
        print(tag)
        print(s)
    elif s_level =="SIMPLE" and (LEVEL =="DETAIL" or LEVEL=="SIMPLE" or LEVEL=="VERY_DETAIL"):
        print(tag)
        print(s)