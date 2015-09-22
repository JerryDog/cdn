__author__ = 'liujiahua'
# coding: UTF-8

import MySQLdb


class CName:
    def __init__(self):
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='', port=3306)
        self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)

    def get_zone(self,domain):
        self.cur.execute('select id from dns.domain where name=%s;', domain)
        _domainid = self.cur.fetchone()
        _domainID = _domainid['id']

        self.cur.execute('select id from dns.domain_zone where domain_id=%s;' , _domainID)
        _domainzone_ids = self.cur.fetchall()
        _domainzone_idl = []
        for _domainzone_id in _domainzone_ids:
            _domainzone_idl.append(str(_domainzone_id['id']))
        return _domainzone_idl

    def insert_cname(self, jrdns, distid):
        _jrdns = jrdns
        _cdndns = distid+'.dlcloud.fastcdn.com.'
        _zone_list = self.get_zone('giantcdn.com')
        self.cur.execute('delete from dns.node where name="%s"' % (_jrdns))
        for _zone in _zone_list:
            self.cur.execute('insert into dns.node(fix,type,ip,domain_id,name) '
                             'values("IN","CNAME","%s","%s","%s")' % (_cdndns, _zone, _jrdns))
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def del_cname(self, jrdns):
        _jrdns = jrdns
        self.cur.execute('delete from dns.node where name=%s', (_jrdns))
        self.conn.commit()
        self.cur.close()
        self.conn.close()
