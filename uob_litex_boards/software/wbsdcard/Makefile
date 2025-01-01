include ../include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak
OBJECTS=wbsdcard.o

all: libwbsdcard.a

print_file_vars:
    $(foreach v, $(.VARIABLES), $(if $(filter file,$(origin $(v))), $(info $(v)=$($(v)))))

libwbsdcard.a: $(OBJECTS)
	$(AR) crs libwbsdcard.a $(OBJECTS)

# pull in dependency info for *existing* .o files
-include $(OBJECTS:.o=.d)

%.o: $(LIBWBSDCARD_DIRECTORY)/%.c
	$(compile)

%.o: %.S
	$(assemble)

.PHONY: all clean

clean:
	$(RM) $(OBJECTS) libwbsdcard.a .*~ *~
