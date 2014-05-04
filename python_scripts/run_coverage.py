from gevent import monkey
monkey.patch_all()
import pymysql
pymysql.install_as_MySQLdb()

from coverage.cmdline import main

main()