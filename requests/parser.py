requests_f = open(
    "/Users/william/Documents/Projects/Smia/smia-kommuneinfo/requests/kommuneinfo_requests.txt", "r")
parsed_f = open(
    "/Users/william/Documents/Projects/Smia/smia-kommuneinfo/requests/requests_parsed.txt", "w")

requests = []

for line in requests_f:
    line_words = line.split(" ")
    # print(line_words)
    try:
        get_idx = line_words.index("\"GET")
        request = line_words[get_idx+1]
        requests.append(request)
    except:
        continue


request_set = set(requests)

for req in request_set:
    parsed_f.write("{}\n".format(req))
