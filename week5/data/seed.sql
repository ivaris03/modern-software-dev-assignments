create table action_items
(
    id          INTEGER not null
        primary key,
    description TEXT    not null,
    completed   BOOLEAN not null
);

create index ix_action_items_completed
    on action_items (completed);

create index ix_action_items_id
    on action_items (id);

create table notes
(
    id         INTEGER      not null
        primary key,
    title      VARCHAR(200) not null,
    content    TEXT         not null,
    created_at DATETIME     not null
);

create index ix_notes_created_at
    on notes (created_at);

create index ix_notes_id
    on notes (id);

create index ix_notes_title
    on notes (title);

create table sqlite_master
(
    type     TEXT,
    name     TEXT,
    tbl_name TEXT,
    rootpage INT,
    sql      TEXT
);

create table tags
(
    id   INTEGER      not null
        primary key,
    name VARCHAR(100) not null
);

create table note_tags
(
    note_id INTEGER not null
        references notes
            on delete cascade,
    tag_id  INTEGER not null
        references tags
            on delete cascade,
    primary key (note_id, tag_id)
);

create index ix_tags_id
    on tags (id);

create unique index ix_tags_name
    on tags (name);