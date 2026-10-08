#include "sqlite3.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <unistd.h>

static void die(sqlite3* db, const std::string& where, int rc=-1) {
  std::cerr << where << " rc=" << rc << " msg=" << (db?sqlite3_errmsg(db):"null") << "\n";
  std::exit(2);
}
static void exec(sqlite3* db, const char* sql) {
  char* err=nullptr; int rc=sqlite3_exec(db,sql,nullptr,nullptr,&err);
  if(rc!=SQLITE_OK){ std::cerr<<"sql="<<sql<<" err="<<(err?err:"")<<"\n"; sqlite3_free(err); die(db,"exec",rc);}
}
static std::string query(sqlite3* db, const char* sql) {
  sqlite3_stmt* s=nullptr; int rc=sqlite3_prepare_v2(db,sql,-1,&s,nullptr); if(rc!=SQLITE_OK)die(db,"prepare",rc);
  rc=sqlite3_step(s); if(rc!=SQLITE_ROW) die(db,"step",rc);
  const unsigned char* p=sqlite3_column_text(s,0); std::string out=p?reinterpret_cast<const char*>(p):"";
  sqlite3_finalize(s); return out;
}
static std::pair<int,int> hdr(const std::filesystem::path& p){std::ifstream f(p,std::ios::binary); std::vector<unsigned char>b(100); f.read((char*)b.data(),b.size()); return {b[18],b[19]};}
static bool exists(const std::string& p){return std::filesystem::exists(p);}
int main(){
  auto dir=std::filesystem::temp_directory_path()/("anonsync-backup-probe-"+std::to_string((long long)getpid()));
  std::filesystem::create_directories(dir);
  std::string src=(dir/"src.sqlite").string(), dst=(dir/"dst.sqlite").string();
  sqlite3 *s=nullptr,*d=nullptr; if(sqlite3_open(src.c_str(),&s)!=SQLITE_OK)die(s,"open src");
  std::cout<<"src mode="<<query(s,"PRAGMA journal_mode=WAL;")<<"\n";
  exec(s,"CREATE TABLE t(x TEXT); INSERT INTO t VALUES('authority');");
  exec(s,"PRAGMA wal_checkpoint(TRUNCATE);");
  auto sh=hdr(src); std::cout<<"src hdr="<<sh.first<<"/"<<sh.second<<" wal="<<exists(src+"-wal")<<" shm="<<exists(src+"-shm")<<"\n";
  if(sqlite3_open(dst.c_str(),&d)!=SQLITE_OK)die(d,"open dst");
  std::cout<<"dst initial mode="<<query(d,"PRAGMA journal_mode;")<<"\n";
  sqlite3_backup* b=sqlite3_backup_init(d,"main",s,"main"); if(!b)die(d,"backup init");
  int step=sqlite3_backup_step(b,-1); int fin=sqlite3_backup_finish(b);
  std::cout<<"backup step="<<step<<" finish="<<fin<<" errmsg="<<sqlite3_errmsg(d)<<"\n";
  auto bh=hdr(dst); std::cout<<"after backup hdr="<<bh.first<<"/"<<bh.second<<" mode-query="<<query(d,"PRAGMA journal_mode;")<<" wal="<<exists(dst+"-wal")<<" shm="<<exists(dst+"-shm")<<"\n";
  std::string switched=query(d,"PRAGMA journal_mode=DELETE;");
  auto ch=hdr(dst); std::cout<<"switch result="<<switched<<" hdr-now="<<ch.first<<"/"<<ch.second<<" mode-query="<<query(d,"PRAGMA journal_mode;")<<" wal="<<exists(dst+"-wal")<<" shm="<<exists(dst+"-shm")<<"\n";
  int frc=sqlite3_db_cacheflush(d); std::cout<<"cacheflush="<<frc<<"\n";
  int rc=sqlite3_close(d); d=nullptr; std::cout<<"close dst="<<rc<<"\n";
  auto ah=hdr(dst); std::cout<<"after close hdr="<<ah.first<<"/"<<ah.second<<" wal="<<exists(dst+"-wal")<<" shm="<<exists(dst+"-shm")<<"\n";
  sqlite3_close(s);
  sqlite3* mem=nullptr; sqlite3_open_v2(":memory:",&mem,SQLITE_OPEN_READONLY|SQLITE_OPEN_MEMORY,nullptr);
  std::ifstream in(dst,std::ios::binary); std::vector<unsigned char> bytes((std::istreambuf_iterator<char>(in)),{});
  auto* owned=(unsigned char*)sqlite3_malloc64(bytes.size()); std::copy(bytes.begin(),bytes.end(),owned);
  rc=sqlite3_deserialize(mem,"main",owned,bytes.size(),bytes.size(),SQLITE_DESERIALIZE_FREEONCLOSE|SQLITE_DESERIALIZE_READONLY);
  std::cout<<"deserialize="<<rc<<" readonly="<<sqlite3_db_readonly(mem,"main")<<"\n";
  sqlite3_stmt* st=nullptr; rc=sqlite3_prepare_v2(mem,"SELECT x FROM t",-1,&st,nullptr);
  std::cout<<"prepare read="<<rc<<" msg="<<sqlite3_errmsg(mem)<<"\n";
  if(rc==SQLITE_OK){rc=sqlite3_step(st); std::cout<<"step read="<<rc<<" value="<<(const char*)sqlite3_column_text(st,0)<<"\n";sqlite3_finalize(st);}
  sqlite3_close(mem);
  std::filesystem::remove_all(dir);
}
