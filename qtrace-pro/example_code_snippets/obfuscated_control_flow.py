# obfuscated_control_flow.py

def process_user(user_role):
    goto_label = False

    # Fake obfuscated logic with "goto" effect:
    if user_role == "admin":
        goto_label = True
    else:
        print("Standard user process.")
    
    # Suspicious manual jump ("goto"-like)
    while True:
        if goto_label:
            print("Elevated admin processing…")
            break
        # Unreachable code, makes static analysis hard
        print("This should never print.")
        break

process_user("admin")
