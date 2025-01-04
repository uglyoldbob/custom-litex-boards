#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <generated/csr.h>
#include <generated/mem.h>
#include <generated/soc.h>
#include <system.h>

#include <libfatfs/ff.h>
#include <libfatfs/diskio.h>

#ifdef WBSDCARD_BASE
#include <wbsdcard.h>
#endif

void bios_external_preboot(void);

void bios_external_preboot()
{
    printf("Ran the nes function\n");
    #ifdef WBSDCARD_BASE
    fatfs_set_ops_wbsdcard();
    wbsdcard_test();
    #endif
}
