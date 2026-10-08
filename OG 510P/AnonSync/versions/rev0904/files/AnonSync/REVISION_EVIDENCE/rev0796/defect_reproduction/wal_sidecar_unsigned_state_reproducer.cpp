#include "anonsync_core_internal.hpp"
#include <sqlite3.h>
#include <openssl/sha.h>
#include <array>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unistd.h>

namespace {
void cleanup(const std::string& p) {
  for (const char* s : {"", "-wal", "-shm", "-journal", ".restore.lock", ".write.lock"}) std::remove((p+s).c_str());
}
std::string file_sha(const std::string& p) {
  std::ifstream in(p, std::ios::binary); if(!in) throw std::runtime_error("open");
  SHA256_CTX ctx; SHA256_Init(&ctx); std::array<char,65536> b{};
  while(in){ in.read(b.data(), b.size()); auto n=in.gcount(); if(n>0) SHA256_Update(&ctx,b.data(),static_cast<size_t>(n)); }
  unsigned char out[SHA256_DIGEST_LENGTH]; SHA256_Final(out,&ctx);
  std::ostringstream o; o<<std::hex<<std::setfill('0'); for(auto c:out)o<<std::setw(2)<<static_cast<unsigned>(c); return o.str();
}
void exec(sqlite3* db, const std::string& sql){char* e=nullptr; if(sqlite3_exec(db,sql.c_str(),nullptr,nullptr,&e)!=SQLITE_OK){std::string m=e?e:sqlite3_errmsg(db);sqlite3_free(e);throw std::runtime_error(m);}}
std::string text(sqlite3* db,const std::string& sql){sqlite3_stmt*s=nullptr;if(sqlite3_prepare_v2(db,sql.c_str(),-1,&s,nullptr)!=SQLITE_OK)throw std::runtime_error(sqlite3_errmsg(db));int rc=sqlite3_step(s);if(rc!=SQLITE_ROW){sqlite3_finalize(s);throw std::runtime_error("no row");}const unsigned char*p=sqlite3_column_text(s,0);int n=sqlite3_column_bytes(s,0);std::string out(reinterpret_cast<const char*>(p),static_cast<size_t>(n));sqlite3_finalize(s);return out;}
anonsync::Json make_case(){using namespace anonsync;Json v;v.type=Json::Type::Object;v.o["case_id"]=json_string_value("wal-sidecar-case");v.o["kind"]=json_string_value("openapi");v.o["operation_id"]=json_string_value("walSidecarOperation");v.o["contract_digest_sha256"]=json_string_value("wal-sidecar-input");v.o["cloud_event_source"]=json_string_value("");v.o["cloud_event_id"]=json_string_value("");return v;}
anonsync::Json make_claims(){using namespace anonsync;Json v;v.type=Json::Type::Object;v.o["operation_id"]=json_string_value("walSidecarOperation");v.o["contract_digest_sha256"]=json_string_value(sha256_hex("wal-sidecar-input"));v.o["jti"]=json_string_value("wal-sidecar-jti");return v;}
}
int main(){
  std::string stem="/tmp/anonsync_rev0792_wal_sidecar_"+std::to_string(::getpid());
  std::string live=stem+"_live.sqlite", snap=stem+"_snapshot.sqlite", dst=stem+"_restored.sqlite";
  cleanup(live);cleanup(snap);cleanup(dst);
  try{
    std::string reason; auto b=anonsync::create_replay_ledger_backend("sqlite-wal"); b->load(live,true,"batch");
    if(!b->stage(make_case(),make_claims(),"allow",reason)||!b->commit(reason)||!b->backup_snapshot(snap,reason)) throw std::runtime_error(reason); b->close();
    sqlite3* db=nullptr; if(sqlite3_open_v2(snap.c_str(),&db,SQLITE_OPEN_READWRITE,nullptr)!=SQLITE_OK) throw std::runtime_error("open snap");
    exec(db,"PRAGMA journal_mode=WAL;"); exec(db,"PRAGMA wal_autocheckpoint=0;"); exec(db,"PRAGMA wal_checkpoint(TRUNCATE);");
    const std::string before=file_sha(snap);
    exec(db,"BEGIN IMMEDIATE; UPDATE effect_outbox SET outbox_state='inflight', dispatch_attempts=1, worker_claim_id='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', worker_id='wal-injected-worker', claimed_at_epoch=100, lease_expires_at_epoch=200 WHERE outbox_state='reserved'; COMMIT;");
    const std::string after=file_sha(snap);
    const auto wal_size=std::filesystem::file_size(snap+"-wal");
    bool accepted=false; std::string error;
    try{anonsync::restore_sqlite_snapshot_into_ledger(snap,dst);accepted=true;}catch(const std::exception&e){error=e.what();}
    std::string state="<none>"; if(accepted){sqlite3* rd=nullptr;sqlite3_open_v2(dst.c_str(),&rd,SQLITE_OPEN_READONLY,nullptr);state=text(rd,"SELECT outbox_state FROM effect_outbox LIMIT 1");sqlite3_close_v2(rd);}
    std::cout<<"main_sha_before="<<before<<"\nmain_sha_after="<<after<<"\nmain_digest_unchanged="<<(before==after?"true":"false")<<"\nwal_size="<<wal_size<<"\nrestore_accepted="<<(accepted?"true":"false")<<"\nrestored_outbox_state="<<state<<"\nerror="<<error<<"\n";
    sqlite3_close_v2(db); cleanup(live);cleanup(snap);cleanup(dst); return 0;
  }catch(const std::exception&e){std::cerr<<"fatal="<<e.what()<<"\n";cleanup(live);cleanup(snap);cleanup(dst);return 2;}
}
