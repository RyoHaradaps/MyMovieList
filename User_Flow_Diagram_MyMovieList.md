# User Flow Diagram for MyMovieList

## Main User Journey Flow

```
┌─────────────────┐
│   Landing Page  │
│   (index.html)  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   User Choice   │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐
│ Browse  │ │ Register│
│ Public  │ │ /Login  │
│Content  │ │         │
└─────────┘ └────┬────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Authentication  │
        │   Process       │
        └─────────┬───────┘
                  │
                  ▼
        ┌─────────────────┐
        │   Home Page     │
        │  (home.html)    │
        └─────────┬───────┘
                  │
                  ▼
        ┌─────────────────┐
        │   Main Menu     │
        └─────────┬───────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
┌─────────┐               ┌─────────┐
│ Search  │               │ Browse  │
│Content  │               │Content  │
└────┬────┘               └────┬────┘
     │                         │
     ▼                         ▼
┌─────────┐               ┌─────────┐
│ Search  │               │Content  │
│Results  │               │Showcase │
└────┬────┘               └────┬────┘
     │                         │
     ▼                         ▼
┌─────────┐               ┌─────────┐
│Content  │               │Content  │
│Detail   │               │Detail   │
│Page     │               │Page     │
└────┬────┘               └────┬────┘
     │                         │
     ▼                         ▼
┌─────────┐               ┌─────────┐
│Add to   │               │Add to   │
│Watchlist│               │Watchlist│
└────┬────┘               └────┬────┘
     │                         │
     ▼                         ▼
┌─────────┐               ┌─────────┐
│Rate &   │               │Rate &   │
│Review   │               │Review   │
└────┬────┘               └────┬────┘
     │                         │
     ▼                         ▼
┌─────────┐               ┌─────────┐
│Profile  │               │Profile  │
│Page     │               │Page     │
└─────────┘               └─────────┘
```

## Detailed User Flow Breakdown

### 1. Registration Flow
```
┌─────────────────┐
│   Register      │
│   Button        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Registration    │
│ Form            │
│ - Username      │
│ - Email         │
│ - Password      │
│ - Birthday      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Validation      │
│ Process         │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐
│Success  │ │Error    │
│Redirect │ │Display  │
│to Home  │ │Message  │
└─────────┘ └─────────┘
```

### 2. Login Flow
```
┌─────────────────┐
│   Login         │
│   Button        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Login Form      │
│ - Username      │
│ - Password      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Authentication  │
│ Check           │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐
│Success  │ │Invalid  │
│Session  │ │Credentials│
│Created  │ │Error    │
└─────────┘ └─────────┘
```

### 3. Content Search Flow
```
┌─────────────────┐
│   Search Bar    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Search Query    │
│ Processing      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Search Results  │
│ Page            │
│ - Movies        │
│ - Series        │
│ - Animated      │
│ - Comics        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Filter Options  │
│ - Genre         │
│ - Year          │
│ - Rating        │
│ - Type          │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Refined Results │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Content Detail  │
│ Selection       │
└─────────────────┘
```

### 4. Watchlist Management Flow
```
┌─────────────────┐
│ Content Detail  │
│ Page            │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Add to List     │
│ Button          │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Status Selection│
│ - Watching      │
│ - Completed     │
│ - On-Hold       │
│ - Dropped       │
│ - Plan to Watch │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Progress Update │
│ (Episodes/Chapters)│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Rating & Review │
│ Entry           │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Save to         │
│ Watchlist       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Profile Page    │
│ (View Lists)    │
└─────────────────┘
```

### 5. Profile Management Flow
```
┌─────────────────┐
│ Profile Page    │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐
│Edit     │ │View     │
│Profile  │ │Lists    │
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│Profile  │ │Watchlist│
│Edit Form│ │Display  │
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│Save     │ │Filter   │
│Changes  │ │Options  │
└─────────┘ └─────────┘
```

## Navigation Flow
```
┌─────────────────┐
│   Navigation    │
│   Bar           │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐
│Home     │ │Search   │
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│Content  │ │Search   │
│Showcase │ │Results  │
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│Profile  │ │Logout   │
└─────────┘ └─────────┘
```

## Error Handling Flow
```
┌─────────────────┐
│   Error         │
│   Occurs        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Error Type      │
│ Detection       │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐
│404      │ │500      │
│Not Found│ │Server   │
│Error    │ │Error    │
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│Custom   │ │Generic  │
│404 Page │ │Error    │
│         │ │Page     │
└─────────┘ └─────────┘
``` 