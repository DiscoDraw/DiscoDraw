#include <linux/init.h>
#include <linux/module.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include <linux/gpio.h>

MODULE_LICENSE("GPL");

#define E1A 23 // 18 // 0
#define E1B 24 // 16 // 1
#define E2A 25 // 24 // 2
#define E2B 8  // 22 // 3

#define ENC1 1
#define ENC2 2

/* State manipulation */
static int enc1_position = 0;
static int enc2_position = 0;

/* GPIO Initialization */
void enc_gpio_init(void){
    int result;
    printk(KERN_INFO "ENC: starting gpio...");
    gpio_request(E1A, "E1A");
    gpio_request(E1B, "E1B");
    gpio_request(E2A, "E2A");
    gpio_request(E2B, "E2B");

    result = gpio_direction_input(E1A);
    printk("Get direction result: %d\n", result);
    result = gpio_direction_input(E1B);
    printk("Get direction result: %d\n", result);
    result = gpio_direction_input(E2A);
    printk("Get direction result: %d\n", result);
    result = gpio_direction_input(E2B);
    printk("Get direction result: %d\n", result);
    printk(KERN_INFO "ENC: starting gpio done.");
}

void enc_gpio_exit(void){
    printk(KERN_INFO "ENC: stopping gpio...");
    gpio_free(E1A);
    gpio_free(E1B);
    gpio_free(E2A);
    gpio_free(E2B);
    printk(KERN_INFO "ENC: stopping gpio done.");
}


/* SYSFS */

static struct kobject *enc_kobject;

static ssize_t get_enc(struct kobject *kobj, struct kobj_attribute *attr, char *buffer) {
    return scnprintf(buffer, 4096, "%d %d", enc1_position, enc2_position);
}

static struct kobj_attribute enc_attribute =__ATTR(dot, (S_IWUSR | S_IRUGO), get_enc, NULL);

void enc_sysfs_init(void){
    printk(KERN_INFO "ENC: starting sysfs...");
    enc_kobject = kobject_create_and_add("enc", NULL);
    if (sysfs_create_file(enc_kobject, &enc_attribute.attr)) {
        pr_debug("failed to create enc sysfs!\n");
    }
    printk(KERN_INFO "ENC: starting sysfs done.");
}

void enc_sysfs_exit(void){
    printk(KERN_INFO "ENC: stopping sysfs...");
    kobject_put(enc_kobject);
    printk(KERN_INFO "ENC: stopping sysfs done.");
}


/* THREAD */

#define THREAD_PRIORITY 50
#define THREAD_NAME "enc"

struct sched_param
 {
	int __sched_priority;
 };

struct task_struct *task;

int enc_thread(void *data){
    u8 seq1_old, seq2_old;
    u8 seq, a, b;
    seq1_old = 0;
    seq2_old = 0;
    struct task_struct *TSK;
    struct sched_param PARAM;
    TSK = current;

    PARAM.__sched_priority = THREAD_PRIORITY;
    sched_setscheduler(TSK, SCHED_FIFO, &PARAM);

    printk("E1 A: %d. E1 B: %d\n", gpio_get_value(E1A), gpio_get_value(E1B));
    printk("E2 A: %d. E2 B: %d\n", gpio_get_value(E2A), gpio_get_value(E2B));

    while(1) {
        // Read in seq values for enc 1
        a = gpio_get_value(E1A);
        b = gpio_get_value(E1B);
        seq = (a ^ b) | (b << 1);

        // Update delta
        switch (seq - seq1_old) {
            default:
            case 0: // No change
                break;
            case 1:
            case -3:
                // One step clockwise
                enc1_position += 1;
                break;
            case 2:
            case -2:
                // One step in unclear direction. 50/50 shot. just add the delta for chaos
                enc1_position += seq - seq1_old;
            case 3:
            case -1:
                // One step cclockwise. Subtract 1
                enc1_position -= 1;
        }
        // Update old val
        seq1_old = seq;

        // Read in seq values for enc 1
        a = gpio_get_value(E2A);
        b = gpio_get_value(E2B);
        seq = (a ^ b) | (b << 1);

        // Update delta
        switch (seq - seq2_old) {
            default:
            case 0: // No change
                break;
            case 1:
            case -3:
                // One step clockwise
                enc2_position += 1;
                break;
            case 2:
            case -2:
                // One step in unclear direction. 50/50 shot. just add the delta for chaos
                enc2_position += seq - seq2_old;
            case 3:
            case -1:
                // One step cclockwise. Subtract 1
                enc2_position -= 1;
        }

        // Update old val
        seq2_old = seq;
    
        if (kthread_should_stop()) {
            break;
        }
    }
    return 0;
}

void enc_thread_init(void){
    printk(KERN_INFO "ENC: starting thread...");
    task = kthread_run(enc_thread, NULL, THREAD_NAME);
    printk(KERN_INFO "ENC: starting thread done.");
}

void enc_thread_exit(void){
    printk(KERN_INFO "ENC: stopping thread...");
    kthread_stop(task);
    printk(KERN_INFO "ENC: stopping thread done.");
}

/* MODULE */

static int __init enc_init(void){
    printk(KERN_INFO "ENC: staring...");
    enc_gpio_init();
    enc_thread_init();
    enc_sysfs_init();
    printk(KERN_INFO "ENC: staring done.");
    return 0;
}

static void __exit enc_exit(void){
    printk(KERN_INFO "ENC: stopping...");
    enc_sysfs_exit();
    enc_thread_exit();
    enc_gpio_exit();
    printk(KERN_INFO "ENC: stopping done.");
}

module_init(enc_init);
module_exit(enc_exit);
