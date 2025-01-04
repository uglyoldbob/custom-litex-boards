include ../include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak
OBJECTS=nes.o

all: libnes.a

print_file_vars:
    $(foreach v, $(.VARIABLES), $(if $(filter file,$(origin $(v))), $(info $(v)=$($(v)))))

libnes.a: $(OBJECTS)
	$(AR) crs libnes.a $(OBJECTS)

# pull in dependency info for *existing* .o files
-include $(OBJECTS:.o=.d)

ifneq ($(LIBWBSDCARD_DIRECTORY),)
    INC := -I$(LIBWBSDCARD_DIRECTORY)
endif

%.o: $(LIBNES_DIRECTORY)/%.c
	 $(CC) -c $(CFLAGS) $(INC) $(1) $< -o $@

%.o: %.S
	$(assemble)

.PHONY: all clean

clean:
	$(RM) $(OBJECTS) libnes.a .*~ *~
