#include <sqlite3.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static void x(sqlite3* db, const char* sql){char* e=0; int rc=sqlite3_exec(db,sql,0,0,&e); if(rc){fprintf(stderr,"sql rc=%d %s (%s)\n",rc,e?e:"",sql); sqlite3_free(e); exit(2);} }
static long long q(sqlite3* db, const char* sql){sqlite3_stmt*s=0; if(sqlite3_prepare_v2(db,sql,-1,&s,0)) exit(3); if(sqlite3_step(s)!=SQLITE_ROW) exit(4); long long v=sqlite3_column_int64(s,0); sqlite3_finalize(s); return v;}
int main(){
 const char* p="/tmp/anonsync-backup-probe.sqlite"; unlink(p); unlink("/tmp/anonsync-backup-probe.sqlite-wal"); unlink("/tmp/anonsync-backup-probe.sqlite-shm");
 sqlite3 *src=0,*wr=0,*dst=0; sqlite3_open_v2(p,&src,SQLITE_OPEN_READWRITE|SQLITE_OPEN_CREATE|SQLITE_OPEN_FULLMUTEX,0); x(src,"PRAGMA journal_mode=WAL; PRAGMA wal_autocheckpoint=0; CREATE TABLE t(x BLOB); BEGIN; INSERT INTO t VALUES(zeroblob(200000)); COMMIT;");
 sqlite3_open_v2(p,&wr,SQLITE_OPEN_READWRITE|SQLITE_OPEN_FULLMUTEX,0); x(wr,"PRAGMA journal_mode=WAL; PRAGMA wal_autocheckpoint=0;");
 long long initial_pages=q(src,"pragma page_count"); long long initial_rows=q(src,"select count(*) from t"); int initial_autocommit=sqlite3_get_autocommit(src); int initial_state=sqlite3_txn_state(src,"main");
 printf("initial pages=%lld rows=%lld autocommit=%d txnstate=%d\n",initial_pages,initial_rows,initial_autocommit,initial_state);
 x(src,"BEGIN;"); printf("after begin ac=%d state=%d\n",sqlite3_get_autocommit(src),sqlite3_txn_state(src,"main"));
 long long pin_pages=q(src,"pragma page_count"); long long pin_rows=q(src,"select count(*) from t"); int pin_state=sqlite3_txn_state(src,"main");
 printf("pin pages=%lld rows=%lld state=%d\n",pin_pages,pin_rows,pin_state);
 sqlite3_open_v2(":memory:",&dst,SQLITE_OPEN_READWRITE|SQLITE_OPEN_CREATE|SQLITE_OPEN_FULLMUTEX|SQLITE_OPEN_MEMORY,0);
 sqlite3_backup* b=sqlite3_backup_init(dst,"main",src,"main"); if(!b){fprintf(stderr,"init %s\n",sqlite3_errmsg(dst)); return 5;}
 int rc=sqlite3_backup_step(b,1); printf("step1 rc=%d pc=%d rem=%d dstpc?skip\n",rc,sqlite3_backup_pagecount(b),sqlite3_backup_remaining(b));
 x(wr,"BEGIN; INSERT INTO t VALUES(zeroblob(4000000)); COMMIT;"); long long writer_pages=q(wr,"pragma page_count"); long long writer_rows=q(wr,"select count(*) from t"); printf("writer pages=%lld rows=%lld\n",writer_pages,writer_rows);
 int n=1; while(rc==SQLITE_OK){rc=sqlite3_backup_step(b,1); ++n; if(n<8 || n%50==0 || rc!=SQLITE_OK) printf("step%d rc=%d pc=%d rem=%d\n",n,rc,sqlite3_backup_pagecount(b),sqlite3_backup_remaining(b)); if(n>5000){puts("too many");break;}}
 int fr=sqlite3_backup_finish(b); long long pinned_rows=q(src,"select count(*) from t"); int finish_state=sqlite3_txn_state(src,"main"); printf("finish=%d steps=%d src rows pin=%lld state=%d\n",fr,n,pinned_rows,finish_state);
 long long dst_rows=q(dst,"select count(*) from t"); long long dst_pages=q(dst,"pragma page_count"); printf("dst rows=%lld pages=%lld\n",dst_rows,dst_pages);
 x(src,"ROLLBACK;"); long long released_rows=q(src,"select count(*) from t"); long long released_pages=q(src,"pragma page_count"); printf("after rollback src rows=%lld pages=%lld\n",released_rows,released_pages);
 sqlite3_close(dst); sqlite3_close(wr); sqlite3_close(src); return 0;
}
