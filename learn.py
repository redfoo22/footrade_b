email_list = [{"name":"foo","age":17,"email":"redfoo@partyrock.com"},{"name":"spirit","age":99,"email":"stopPlaying@gmail.com"}]

user = {"name":"jaz","age":34,"email":"jaz@partyrock.com"}

for anything in range(10):
    email_list.append(user)



for obj in email_list:
    print(obj["name"],obj["age"],obj["email"])