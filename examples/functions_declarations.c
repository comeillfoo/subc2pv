void boo0();
void boo1(int x);
void boo2(int x, int y);
void boo3(int x, int y, int z);
void boo4(int* x);
void boo5(const int* x);
void boo6(int const* x);
void boo7(int* const x);
void boo8(int* restrict x, int* restrict y);
void boo9(int* restrict x, int* restrict y, ...);

int foo0();
int foo1(int x);
int foo2(int x, int y);
int foo3(int x, int y, int z);
int foo4(int* x);
int foo5(const int* x);
int foo6(int const* x);
int foo7(int* const x);
int foo8(int* restrict x, int* restrict y);
int foo9(int* restrict x, int* restrict y, ...);

static int bar0();
static int bar1(int x);
static int bar2(int x, int y);
static int bar3(int x, int y, int z);
static int bar4(int* x);
static int bar5(const int* x);
static int bar6(int const* x);
static int bar7(int* const x);
static int bar8(int* restrict x, int* restrict y);
static int bar9(int* restrict x, int* restrict y, ...);

inline int baz0();
inline int baz1(int x);
inline int baz2(int x, int y);
inline int baz3(int x, int y, int z);
inline int baz4(int* x);
inline int baz5(const int* x);
inline int baz6(int const* x);
inline int baz7(int* const x);
inline int baz8(int* restrict x, int* restrict y);
inline int baz9(int* restrict x, int* restrict y, ...);

static inline int bug0();
static inline int bug1(int x);
static inline int bug2(int x, int y);
static inline int bug3(int x, int y, int z);
static inline int bug4(int* x);
static inline int bug5(const int* x);
static inline int bug6(int const* x);
static inline int bug7(int* const x);
static inline int bug8(int* restrict x, int* restrict y);
static inline int bug9(int* restrict x, int* restrict y, ...);

extern inline int bud0();
extern inline int bud1(int x);
extern inline int bud2(int x, int y);
extern inline int bud3(int x, int y, int z);
extern inline int bud4(int* x);
extern inline int bud5(const int* x);
extern inline int bud6(int const* x);
extern inline int bud7(int* const x);
extern inline int bud8(int* restrict x, int* restrict y);
extern inline int bud9(int* restrict x, int* restrict y, ...);

extern static int fee0();
extern static int fee1(int x);
extern static int fee2(int x, int y);
extern static int fee3(int x, int y, int z);
extern static int fee4(int* x);
extern static int fee5(const int* x);
extern static int fee6(int const* x);
extern static int fee7(int* const x);
extern static int fee8(int* restrict x, int* restrict y);
extern static int fee9(int* restrict x, int* restrict y, ...);

extern static inline int kaz0();
extern static inline int kaz1(int x);
extern static inline int kaz2(int x, int y);
extern static inline int kaz3(int x, int y, int z);
extern static inline int kaz4(int* x);
extern static inline int kaz5(const int* x);
extern static inline int kaz6(int const* x);
extern static inline int kaz7(int* const x);
extern static inline int kaz8(int* restrict x, int* restrict y);
extern static inline int kaz9(int* restrict x, int* restrict y, ...);

extern static inline void* buzz0();
extern static inline void* buzz1(int x);
extern static inline void* buzz2(int x, int y);
extern static inline void* buzz3(int x, int y, int z);
extern static inline void* buzz4(int* x);
extern static inline void* buzz5(const int* x);
extern static inline void* buzz6(int const* x);
extern static inline void* buzz7(int* const x);
extern static inline void* buzz8(int* restrict x, int* restrict y);
extern static inline void* buzz9(int* restrict x, int* restrict y, ...);
