#
# 创建库表
#

use philosophy;

CREATE TABLE if not exists backup_t
(
	id integer primary key not null auto_increment,
	t_key varchar(1024) comment 'KEY',
	t_value text comment 'VALUE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
