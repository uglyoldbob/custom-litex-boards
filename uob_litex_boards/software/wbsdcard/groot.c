#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <generated/csr.h>
#include <generated/mem.h>
#include <generated/soc.h>
#include <system.h>

#include <libfatfs/ff.h>
#include <libfatfs/diskio.h>
#include "wbsdcard.h"

#include "bios/command.h"

static void sdcard_test(int nb_params, char **params)
{
	printf("SDCard test I am groot\n");
}

define_command(groot_detect, sdcard_test, "Detect groot", LITESDCARD_CMDS);
