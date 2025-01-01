#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <generated/csr.h>
#include <generated/mem.h>
#include <generated/soc.h>
#include <system.h>

#include <libfatfs/ff.h>
#include <libfatfs/diskio.h>

#include <wbsdcard.h>

void bios_external_preboot(void);

void bios_external_preboot()
{
    printf("Ran the nes function\n");
    fatfs_set_ops_wbsdcard();
    wbsdcard_test();
}
