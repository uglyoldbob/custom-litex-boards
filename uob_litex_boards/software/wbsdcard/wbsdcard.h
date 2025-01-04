#ifndef __SDCARD_H
#define __SDCARD_H

#ifdef __cplusplus
extern "C" {
#endif

#include <generated/csr.h>

void wbsdcard_test(void);
void fatfs_set_ops_wbsdcard(void);

#ifdef __cplusplus
}
#endif

#endif /* __SDCARD_H */

