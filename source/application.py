import lib.prototype as p

role = input("Run as (bug/client): ").lower()

if role == 'bug':
    server = p.Bug()
    server.run()
elif role == 'client':
    client = p.Client()
    client.handle_bug()
else:
    print("Invalid role. Please select 'bug' or 'client'.")