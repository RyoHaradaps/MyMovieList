# Entity-Relationship Diagram for MyMovieList

## Database Schema Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Profile     │    │   BaseContent   │    │     Genre       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ PK: id          │    │ PK: id          │    │ PK: id          │
│ username (UK)   │    │ title           │    │ name (UK)       │
│ email (UK)      │    │ alt_title       │    └─────────────────┘
│ password        │    │ synonyms        │             │
│ birthday        │    │ description     │             │
│ avatar          │    │ poster_url      │             │
│ bio             │    │ rating          │             │
│ join_date       │    │ release_year    │             │
│ gender          │    │ content_type    │             │
│ last_online     │    │ tmdb_id         │             │
└─────────────────┘    │ created_at      │             │
         │             └─────────────────┘             │
         │                      │                      │
         │                      │                      │
         │                      ▼                      │
         │             ┌─────────────────┐             │
         │             │ BaseContent_Genres │         │
         │             ├─────────────────┤             │
         │             │ FK: basecontent_id │         │
         │             │ FK: genre_id     │             │
         │             └─────────────────┘             │
         │                      │                      │
         │                      │                      │
         ▼                      │                      │
┌─────────────────┐             │                      │
│    Watchlist    │             │                      │
├─────────────────┤             │                      │
│ PK: id          │             │                      │
│ FK: profile_id  │◄────────────┼──────────────────────┼──┐
│ FK: content_id  │             │                      │  │
│ status          │             │                      │  │
│ score           │             │                      │  │
│ progress        │             │                      │  │
│ review          │             │                      │  │
│ added_on        │             │                      │  │
│ rewatched       │             │                      │  │
│ reread          │             │                      │  │
└─────────────────┘             │                      │  │
                                │                      │  │
                                ▼                      │  │
                       ┌─────────────────┐             │  │
                       │ ContentRelation │             │  │
                       ├─────────────────┤             │  │
                       │ PK: id          │             │  │
                       │ FK: from_content│◄────────────┼──┘
                       │ FK: to_content  │             │
                       │ relation_type   │             │
                       └─────────────────┘             │
                                │                      │
                                │                      │
                                ▼                      │
                       ┌─────────────────┐             │
                       │    Character    │             │
                       ├─────────────────┤             │
                       │ PK: id          │             │
                       │ name            │             │
                       │ description     │             │
                       │ image_url       │             │
                       │ FK: content_id  │◄────────────┼──┐
                       └─────────────────┘             │  │
                                │                      │  │
                                │                      │  │
                                ▼                      │  │
                       ┌─────────────────┐             │  │
                       │ Character_BaseContent │       │  │
                       ├─────────────────┤             │  │
                       │ FK: character_id│             │  │
                       │ FK: basecontent_id │          │  │
                       └─────────────────┘             │  │
                                │                      │  │
                                │                      │  │
                                ▼                      │  │
                       ┌─────────────────┐             │  │
                       │   VoiceActor    │             │  │
                       ├─────────────────┤             │  │
                       │ PK: id          │             │  │
                       │ name            │             │  │
                       │ language        │             │  │
                       │ image_url       │             │  │
                       └─────────────────┘             │  │
                                │                      │  │
                                │                      │  │
                                ▼                      │  │
                       ┌─────────────────┐             │  │
                       │ VoiceActor_Character │        │  │
                       ├─────────────────┤             │  │
                       │ FK: voiceactor_id│            │  │
                       │ FK: character_id│             │  │
                       └─────────────────┘             │  │
                                │                      │  │
                                │                      │  │
                                ▼                      │  │
                       ┌─────────────────┐             │  │
                       │     Staff       │             │  │
                       ├─────────────────┤             │  │
                       │ PK: id          │             │  │
                       │ name            │             │  │
                       │ role            │             │  │
                       │ image_url       │             │  │
                       └─────────────────┘             │  │
                                │                      │  │
                                │                      │  │
                                ▼                      │  │
                       ┌─────────────────┐             │  │
                       │ Staff_BaseContent │           │  │
                       ├─────────────────┤             │  │
                       │ FK: staff_id    │             │  │
                       │ FK: basecontent_id │          │  │
                       └─────────────────┘             │  │
                                │                      │  │
                                │                      │  │
                                ▼                      │  │
                       ┌─────────────────┐             │  │
                       │     Theme       │             │  │
                       ├─────────────────┤             │  │
                       │ PK: id          │             │  │
                       │ name            │             │  │
                       │ description     │             │  │
                       └─────────────────┘             │  │
                                │                      │  │
                                │                      │  │
                                ▼                      │  │
                       ┌─────────────────┐             │  │
                       │ Theme_BaseContent │           │  │
                       ├─────────────────┤             │  │
                       │ FK: theme_id    │             │  │
                       │ FK: basecontent_id │          │  │
                       └─────────────────┘             │  │
                                │                      │  │
                                │                      │  │
                                └──────────────────────┼──┘
                                                       │
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   BaseContent   │
                                              │   (Self-Relation) │
                                              └─────────────────┘
```

## Key Relationships:

1. **Profile ↔ Watchlist**: One-to-Many (One user can have multiple watchlist entries)
2. **BaseContent ↔ Watchlist**: One-to-Many (One content can be in multiple users' watchlists)
3. **BaseContent ↔ Genre**: Many-to-Many (Content can have multiple genres, genres can belong to multiple content)
4. **BaseContent ↔ Character**: Many-to-Many (Content can have multiple characters, characters can appear in multiple content)
5. **Character ↔ VoiceActor**: Many-to-Many (Characters can have multiple voice actors, voice actors can voice multiple characters)
6. **BaseContent ↔ Staff**: Many-to-Many (Content can have multiple staff members, staff can work on multiple content)
7. **BaseContent ↔ Theme**: Many-to-Many (Content can have multiple themes, themes can apply to multiple content)
8. **BaseContent ↔ ContentRelation**: Self-referencing (Content can be related to other content)

## Content Types Supported:
- Movie
- Series  
- Animated Show
- Comic/Cartoon

## Status Types for Watchlist:
- Watching
- Completed
- On-Hold
- Dropped
- Plan to Watch/Read 