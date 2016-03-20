
def get_ip_top(file_name, top_size, ip_position=0, separate=' '):
    ip_data = {}
    with open(file_name) as f:

        for line in f:
            values = line.split(separate)
            ip_value = values[ip_position]

            if ip_value not in ip_data:
                ip_data[ip_value] = 1
            else:
                ip_data[ip_value] += 1

    ip_top = sorted(ip_data.items(), key=lambda x: x[1], reverse=True)

    for record in ip_top[:top_size]:
        print('{0}: {1}'.format(record[1], record[0]))

if __name__ == '__main__':
    get_ip_top('access.log', 10)
