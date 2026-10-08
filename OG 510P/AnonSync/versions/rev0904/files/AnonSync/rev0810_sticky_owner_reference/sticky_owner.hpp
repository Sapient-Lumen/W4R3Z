#pragma once
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>
namespace anonsync::rev0810 {
struct Proof { std::string owner; std::uint64_t generation; };
class Reservation final {
 public: std::uint64_t generation() const noexcept { return generation_; }
 private: explicit Reservation(std::uint64_t g):generation_(g){} std::uint64_t generation_; friend class StickyOwner;
};
class StickyOwner final {
 public:
  std::uint64_t establish(std::string owner) { if(ever_ && !disabled_) throw 1; owner_=std::move(owner); ever_=true; disabled_=false; active_=true; return ++generation_; }
  bool release(const Proof& p) { if(!matches(p)||disabled_) return false; active_=false; return true; }
  std::optional<Reservation> reserve(const std::optional<Proof>& p=std::nullopt) const { if(ever_&&!disabled_) { if(!p||!matches(*p)) return std::nullopt; return Reservation(generation_); } if(p) return std::nullopt; return Reservation(0); }
  bool reset(const Reservation& r) { if(ever_&&!disabled_) return r.generation_==generation_; return r.generation_==0; }
  bool disable(const Proof& p,bool verified_admin_evidence) { if(!verified_admin_evidence||!matches(p)||disabled_) return false; active_=false; disabled_=true; return true; }
  std::uint64_t generation() const noexcept{return generation_;} bool active() const noexcept{return active_;} bool ever_owned() const noexcept{return ever_;}
 private: bool matches(const Proof&p)const{return p.owner==owner_&&p.generation==generation_&&generation_!=0;} std::string owner_; std::uint64_t generation_=0; bool ever_=false,active_=false,disabled_=false;
};
}
