# coding=utf-8
import re

def parse_summary_info_by_html(f_html):
    try:
        f = open(f_html)
    except:
        return None

    s = f.read()
    f.close()

    u = s.decode('ISO-8859-1')

    pre_title_pos = u.find(u'<H2>OVERALL COVERAGE SUMMARY</H2>')
    pre_title_len = len(u'<H2>OVERALL COVERAGE SUMMARY</H2>')
    next_title_pos = u.find(u'<H3>OVERALL STATS SUMMARY</H3>')

    cov_sum_info = u[pre_title_pos + pre_title_len : next_title_pos]
    cov_datas = re.findall(u'>(\d+%)', cov_sum_info)

    ret = {
        u'class_cov': cov_datas[0],
        u'method_cov': cov_datas[1],
        u'block_cov': cov_datas[2],
        u'line_cov': cov_datas[3],
    }

    return ret

if __name__ == '__main__':
    ret = parse_summary_info_by_html('./index.html')
    print ret
