drop table if exists users;
create table users (
  id integer primary key autoincrement,
  user_login string not null,
  user_password string not null,
  user_display_name string not null,
  user_level integer not null
);
