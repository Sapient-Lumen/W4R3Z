#include "sticky_owner.hpp"
#include <cassert>
#include <type_traits>
int main(){using namespace anonsync::rev0810; static_assert(!std::is_default_constructible_v<Reservation>); StickyOwner s; auto free=s.reserve(); assert(free&&s.reset(*free)); auto g=s.establish("a"); Proof p{"a",g}; assert(!s.reserve()); auto r=s.reserve(p); assert(r); assert(s.release(p)); assert(!s.reserve()); assert(s.reserve(p)); assert(s.reset(*r)); assert(s.ever_owned()&&s.generation()==g&&!s.active()); assert(s.disable(p,true)); assert(s.reserve()); auto g2=s.establish("b"); assert(g2==g+1); assert(!s.reserve(p)); return 0;}
