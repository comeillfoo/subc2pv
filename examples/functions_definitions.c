void boo0() { }
void boo1(int x) { }
void boo2(int x, int y) { }
void boo3(int x, int y, int z) { }
void boo4(int* x) { }
void boo5(const int* x) { }
void boo6(int const* x) { }
void boo7(int* const x) { }
void boo8(int* restrict x, int* restrict y) { }

int foo0() { }
int foo1(int x) { }
int foo2(int x, int y) { }
int foo3(int x, int y, int z) { }
int foo4(int* x) { }
int foo5(const int* x) { }
int foo6(int const* x) { }
int foo7(int* const x) { }
int foo8(int* restrict x, int* restrict y) { }

static int bar0() { }
static int bar1(int x) { }
static int bar2(int x, int y) { }
static int bar3(int x, int y, int z) { }
static int bar4(int* x) { }
static int bar5(const int* x) { }
static int bar6(int const* x) { }
static int bar7(int* const x) { }
static int bar8(int* restrict x, int* restrict y) { }

inline int baz0() { }
inline int baz1(int x) { }
inline int baz2(int x, int y) { }
inline int baz3(int x, int y, int z) { }
inline int baz4(int* x) { }
inline int baz5(const int* x) { }
inline int baz6(int const* x) { }
inline int baz7(int* const x) { }
inline int baz8(int* restrict x, int* restrict y) { }

static inline int bug0() { }
static inline int bug1(int x) { }
static inline int bug2(int x, int y) { }
static inline int bug3(int x, int y, int z) { }
static inline int bug4(int* x) { }
static inline int bug5(const int* x) { }
static inline int bug6(int const* x) { }
static inline int bug7(int* const x) { }
static inline int bug8(int* restrict x, int* restrict y) { }

static inline void* buzz0() { }
static inline void* buzz1(int x) { }
static inline void* buzz2(int x, int y) { }
static inline void* buzz3(int x, int y, int z) { }
static inline void* buzz4(int* x) { }
static inline void* buzz5(const int* x) { }
static inline void* buzz6(int const* x) { }
static inline void* buzz7(int* const x) { }
static inline void* buzz8(int* restrict x, int* restrict y) { }
